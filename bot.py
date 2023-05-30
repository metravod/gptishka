import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from gpt_connector import GPTConnector
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
async def start_new_chat(message: types.Message):
    contexts = orm.get_list_contexts_by_user(message.from_user.id)
    markup = forming_inline_lists(contexts)
    await message.answer('Вот список твоих контекстов', reply_markup=markup)


@dp.callback_query_handler()
async def choose_chat(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    chat = orm.get_context(callback_query.from_user.id, callback_query.data)
    cli.set(callback_query.from_user.id, chat.content)
    await bot.send_message(callback_query.from_user.id, f'Погнали!', reply_markup=END_CHAT)
    await Chat.content.set()


@dp.message_handler(state=Chat.content)
async def chating(message: types.Message, state: FSMContext):
    print(f'!!! >>> {message.text}')
    await state.update_data(content=message.text)
    user_id = message.from_user.id

    if message.text == 'Завершить чат':
        await message.answer('Сохранить текущую беседу или удалить?', reply_markup=ENDED_CHAT)
        await state.finish()
        await DecissionChat.content.set()

    else:
        chat = cli.get(user_id)
        print(f'from redis >>> {chat}')
        chat = [chat] if isinstance(chat, dict) else chat
        print(f'after listing >>> {chat}')
        chat.append(forming_message('user', message.text))
        print(f' after append {chat}')
        answer, tokens = GPTConnector(chat).run()

        chat.append(forming_message('assistant', message.text))
        cli.set(user_id, chat)

        await message.answer(answer, reply_markup=END_CHAT)
        await state.finish()
        await Chat.content.set()


@dp.message_handler(state=DecissionChat.content)
async def decission_end_context(message: types.Message, state: FSMContext):
    if message.text == 'Сохранить':
        chat = cli.get(message.from_user.id)
        orm.save_context(message.from_user.id, 'test', chat)
        cli.delete(message.from_user.id)
        await state.finish()
        await message.answer('Готово, можешь начать новый диалог', reply_markup=MAIN_MENU)
    elif message.text == 'Удалить':
        cli.delete(message.from_user.id)
        await state.finish()
        await message.answer('Готово, можешь начать новый диалог', reply_markup=MAIN_MENU)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
