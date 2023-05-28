from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from gpt_connector import GPTConnector
from redis_helper import RedisHelper
from settings.bot_config import bot_token
from settings.common import base_context, forming_message
from database import orm

bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

cli = RedisHelper()


class Chat(StatesGroup):
    content = State()


class CustomContext(StatesGroup):
    content = State()


class DecissionChat(StatesGroup):
    content = State()


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    orm.add_user(message.from_user.id)
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Новый чат - базовый контекст')
    btn2 = types.KeyboardButton('Новый чат - свой контекст')
    btn3 = types.KeyboardButton('Список сохранённых чатов')
    markup.add(btn1, btn2, btn3)
    text = f'Привет {message.from_user.first_name}, я бот, который поможет тебе взаимодействовать с ChatGPT'
    await message.answer(text, reply_markup=markup)


@dp.message_handler(regexp='Новый чат - базовый контекст')
async def new_base_chat(message: types.Message):
    cli.set(message.from_user.id, base_context)
    await message.answer('Погнали')
    await Chat.content.set()


@dp.message_handler(regexp='Новый чат - свой контекст')
async def custom_context(message: types.Message):
    await message.answer('Какой контекст задать?')
    await CustomContext.content.set()


@dp.message_handler(state=CustomContext.content)
async def new_base_chat(message: types.Message, state: FSMContext):
    await state.update_data(content=message.text)
    cli.set(message.from_user.id, forming_message('system', message.text))
    await message.answer('Погнали')
    await Chat.content.set()


@dp.message_handler(regexp='Список сохранённых чатов')
async def start_new_chat(message: types.Message):
    ...


@dp.message_handler(state=Chat.content)
async def chating(message: types.Message, state: FSMContext):
    await state.update_data(content=message.text)
    user_id = message.from_user.id

    if message.text == 'Завершить чат':
        markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=1)
        btn1 = types.KeyboardButton('Сохранить')
        btn2 = types.KeyboardButton('Удалить')
        markup.add(btn1, btn2)
        await message.answer('Сохранить текущую беседу или удалить?', reply_markup=markup)
        await DecissionChat.content.set()

    else:
        chat = cli.get(user_id)
        chat.append(forming_message('user', message.text))
        print(chat)
        answer, tokens = GPTConnector(chat).run()

        chat.append(forming_message('assistant', message.text))
        cli.set(user_id, chat)

        markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=1)
        btn1 = types.KeyboardButton('Завершить чат')
        markup.add(btn1)

        await message.answer(answer, reply_markup=markup)
        await state.finish()
        await Chat.content.set()


@dp.message_handler(regexp='Сохранить')
async def chating(message: types.Message):
    chat = cli.get(message.from_user.id)
    orm.save_context(message.from_user.id, 'test', chat)
    cli.delete(message.from_user.id)
    await message.answer('Готово, можешь начать новый диалог')


@dp.message_handler(regexp='Удалить')
async def chating(message: types.Message):
    cli.delete(message.from_user.id)
    await message.answer('Готово, можешь начать новый диалог')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
