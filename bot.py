from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from gpt_connector import GPTConnector
from settings.bot_config import bot_token
from settings.common import base_context, forming_message, message_context_full
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

    # Получаем сообщение, определяем юзера и чат
    await state.update_data(content=message.text)
    user_id = message.from_user.id
    chat = orm.get_active_context(user_id)

    # Если в текущем контексте больше 4090 токенов (ограничение API),
    # то мы его деактивируем, потому что работать он больше уже не будет
    if chat.tokens > 4090:
        orm.disactive_context(user_id, chat.name)
        chat = None

    # Если активный чат не найден, то создаём новый и делаем активным его
    if chat is None:
        orm.add_context(message.from_user.id, 'test', 1, True)
        orm.add_message(user_id, 'test', base_context)
        chat = orm.get_active_context(user_id)

    # На случай необходимости прекратить беседу
    if message.text == 'exit':
        await message.answer('Пока!')
        await state.finish()

    # Тащим весь контекст
    context = orm.get_talk(user_id, chat.name)

    # Собираем сообщение и добавляем его в беседу
    msg = forming_message('user', message.text)
    orm.add_message(user_id, chat.name, msg)
    context.append(forming_message('user', message.text))

    # Скармливаем контекст gpt
    try:
        answer, tokens = GPTConnector(context).run()
    except:
        await message.answer(message_context_full)
        await state.finish()

    # Добавляем ответ к контексту и сохраняем
    orm.update_count_tokens_in_context(user_id, chat.name, tokens)
    gpt_msg = forming_message('assistant', answer)
    orm.add_message(user_id, chat.name, gpt_msg)

    await message.answer(answer)
    await state.finish()
    await BaseChat.content.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
