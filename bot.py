import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from gpt_connector import GPTConnector, define_name_chat
from redis_helper import RedisHelper
from settings.bot_config import bot_token
from settings.common import base_context, forming_message
from database import orm
from bot_markup import MAIN_MENU, END_CHAT, ENDED_CHAT, forming_inline_lists

bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

cli = RedisHelper()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class Chat(StatesGroup):
    content = State()


class CustomContext(StatesGroup):
    content = State()


class DecissionChat(StatesGroup):
    content = State()


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
    cli.set(message.from_user.id, forming_message('system', message.text))
    await message.answer('Погнали', reply_markup=END_CHAT)
    await Chat.content.set()


@dp.message_handler(regexp='Список сохранённых чатов')
async def get_list_contexts(message: types.Message):
    contexts = orm.get_list_contexts_by_user(message.from_user.id)
    markup = forming_inline_lists(contexts)
    await message.answer('Вот список твоих контекстов', reply_markup=markup)


@dp.callback_query_handler()
async def choose_chat(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    chat = orm.get_context(user_id, callback_query.data)
    cli.set(user_id, chat.content)
    cli.set(f'{user_id}_active', chat.name)
    await bot.send_message(callback_query.from_user.id, f'Погнали!', reply_markup=END_CHAT)
    await Chat.content.set()


@dp.message_handler(state=Chat.content)
async def chating(message: types.Message, state: FSMContext):
    await state.update_data(content=message.text)
    user_id = message.from_user.id

    if message.text == 'Завершить чат':
        await message.answer('Сохранить текущую беседу или удалить?', reply_markup=ENDED_CHAT)
        await state.finish()
        await DecissionChat.content.set()

    else:
        if cli.get(f'{user_id}_active') is None:
            cli.set(f'{user_id}_active', define_name_chat(message.text))
        chat = cli.get(user_id)
        chat = [chat] if isinstance(chat, dict) else chat
        chat.append(forming_message('user', message.text))
        answer, tokens = GPTConnector(chat).run()

        chat.append(forming_message('assistant', message.text))
        cli.set(user_id, chat)

        await message.answer(answer, reply_markup=END_CHAT)
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
