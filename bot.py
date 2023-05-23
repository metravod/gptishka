from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from gpt_connector import GPTConnector
from settings.bot_config import bot_token
from settings.common import base_context, forming_message
from database import orm

bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class BaseChat(StatesGroup):
    content = State()


class NameChat(StatesGroup):
    name = State()


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    orm.add_user(message.from_user.id)
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Новый чат')
    btn2 = types.KeyboardButton('Список сохранённых чатов')
    markup.add(btn1, btn2)
    text = f'Привет {message.from_user.first_name}, я бот, который поможет тебе взаимодействовать с ChatGPT'
    await message.answer(text, reply_markup=markup)


@dp.message_handler(regexp='Новый чат')
async def new_chat(message: types.Message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Погнали с базовым контекстом')
    btn2 = types.KeyboardButton('Задать начальный контекст')
    markup.add(btn1, btn2)
    text = f'Как стартуем?'
    await message.answer(text, reply_markup=markup)


@dp.message_handler(regexp='Погнали с базовым контекстом')
async def start_new_chat(message: types.Message):
    await message.answer('Погнали')
    await BaseChat.content.set()


@dp.message_handler(state=BaseChat.content)
async def chating(message: types.Message, state: FSMContext):
    print('go >>> ', state)
    await state.update_data(content=message.text)
    user_id = message.from_user.id
    chat = orm.get_active_context(user_id)

    if chat is None:
        orm.add_context(message.from_user.id, 'test', 1, True)
        orm.add_message(user_id, 'test', base_context)
        chat = orm.get_active_context(user_id)

    if message.text != 'exit':
        context = orm.get_talk(user_id, chat.name)

        msg = forming_message('user', message.text)
        orm.add_message(user_id, chat.name, msg)
        context.append(forming_message('user', message.text))

        answer, tokens = GPTConnector(context).run()

        orm.update_count_tokens_in_context(user_id, chat.name, tokens)
        gpt_msg = forming_message('assistant', answer)
        orm.add_message(user_id, chat.name, gpt_msg)

        await message.answer(answer)
        await state.finish()
        await BaseChat.content.set()
    else:
        await message.answer('Пока!')
        await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
