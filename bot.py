import os
import sys
import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from gpt_connector import GPTConnector, define_name_chat
from database.redis_helper import RedisHelper
# from settings.bot_config import bot_token, admin_id
from settings.common import base_context, forming_message
from database import orm
from bot_markup import MAIN_MENU, END_CHAT, ENDED_CHAT, EXTRACT_CODE, CREATE_GISTS, forming_inline_lists
from tools.message_formater import MessageFormatter, extracting_code
from tools.gist_creator import GistCreator

bot_token = os.getenv('BOT')
admin_id = os.getenv('ADMIN')

bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

cli = RedisHelper()

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


class Chat(StatesGroup):
    content = State()


class CustomContext(StatesGroup):
    content = State()


class DecissionChat(StatesGroup):
    content = State()


@dp.errors_handler()
async def error(update, err):
    await bot.send_message(chat_id=admin_id, text=f'Там всё упало - {type(err).__name__}: {err}')


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    orm.add_user(message.from_user.id)
    text = f'Привет {message.from_user.first_name}, я бот, который поможет тебе взаимодействовать с ChatGPT'
    await message.answer(text, reply_markup=MAIN_MENU)


@dp.message_handler(regexp='Новый чат - базовый контекст')
async def new_base_chat(message: types.Message):
    cli.set(message.from_user.id, base_context)
    await message.answer('Погнали', reply_markup=END_CHAT)
    await Chat.content.set()


@dp.message_handler(regexp='Новый чат - свой контекст')
async def custom_context(message: types.Message):
    await message.answer('Какой контекст задать?')
    await CustomContext.content.set()


@dp.message_handler(state=CustomContext.content)
async def new_base_chat(message: types.Message, state: FSMContext):
    await state.update_data(content=message.text)
    cli.set(message.from_user.id, forming_message(role='system', text=message.text))
    await message.answer(text='Погнали', reply_markup=END_CHAT)
    await Chat.content.set()


@dp.message_handler(regexp='Список сохранённых чатов')
async def get_list_contexts(message: types.Message):
    contexts = orm.get_list_contexts_by_user(message.from_user.id)
    if len(contexts) > 0:
        markup = forming_inline_lists(contexts)
        await message.answer(text='Вот список твоих контекстов', reply_markup=markup)
    else:
        await message.answer('У тебя нет сохранённых контекстов')


@dp.callback_query_handler()
async def choose_chat(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    chat = orm.get_context(user_id, ctx_id=callback_query.data)
    cli.set(user_id, chat.content)
    cli.set(key=f'{user_id}_active', value=chat.name)
    await bot.send_message(callback_query.from_user.id, text=f'Погнали!', reply_markup=END_CHAT)
    await Chat.content.set()


@dp.message_handler(state=Chat.content)
async def chating(message: types.Message, state: FSMContext):
    await state.update_data(content=message.text)
    user_id = message.from_user.id

    if message.text == 'Завершить чат':
        await message.answer(text='Сохранить текущую беседу или удалить?', reply_markup=ENDED_CHAT)
        await state.finish()
        await DecissionChat.content.set()

    elif message.text == 'Вытащи код':
        # Достаем из редиса последнее сообщение
        chat = cli.get(user_id)
        last_msg = chat[-1]
        just_code = extracting_code(last_msg['content'])

        chat.append(forming_message(role='assistant', text=just_code))
        cli.set(user_id, chat)

        await message.answer(text=just_code, reply_markup=CREATE_GISTS)
        await state.finish()
        await Chat.content.set()

    elif message.text == 'Создай gists':
        last_msg = cli.get(user_id)[-1]
        url = GistCreator(last_msg['content']).post()
        await message.answer(text=url, reply_markup=END_CHAT)
        await state.finish()
        await Chat.content.set()

    else:
        if cli.get(f'{user_id}_active') is None:
            cli.set(key=f'{user_id}_active', value=define_name_chat(message.text))
        chat = cli.get(user_id)
        chat = [chat] if isinstance(chat, dict) else chat
        chat.append(forming_message(role='user', text=message.text))
        answer, tokens = GPTConnector(chat).run()

        answer, its_a_code = MessageFormatter(answer).formating()

        chat.append(forming_message(role='assistant', text=answer))
        cli.set(user_id, chat)

        # Для сообщений с кодом добавляем в менюшку
        # кнопку с просьбой вернуть только код
        markup = EXTRACT_CODE if its_a_code else END_CHAT

        await message.answer(answer, reply_markup=markup)
        await state.finish()
        await Chat.content.set()


@dp.message_handler(state=DecissionChat.content)
async def decission_end_context(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    name_chat = cli.get(f'{user_id}_active')
    if message.text == 'Сохранить':
        chat = cli.get(user_id)
        orm.save_context(user_id, name_chat, chat)
        cli.delete(user_id)
        cli.delete(f'{user_id}_active')
        await state.finish()
        await message.answer('Сохранил, можешь начать новый диалог', reply_markup=MAIN_MENU)
    elif message.text == 'Удалить':
        cli.delete(user_id)
        cli.delete(f'{user_id}_active')
        orm.delete_user_context(user_id, name_chat)
        await state.finish()
        await message.answer('Удалил, можешь начать новый диалог', reply_markup=MAIN_MENU)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
