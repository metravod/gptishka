import os
import sys
import logging
import asyncio

from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.types import ErrorEvent, Message, CallbackQuery

from gpt_connector import GPTConnector, define_name_chat
from database import orm
from database.redis_helper import RedisHelper
from bot_markup import MAIN_MENU, END_CHAT, ENDED_CHAT, EXTRACT_CODE, CREATE_GISTS, forming_inline_lists
from tools.message_formater import MessageFormatter, extracting_code, base_context, forming_message
from tools.gist_creator import GistCreator

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

bot_token = os.getenv('BOT_TOKEN')
admin_id = os.getenv('ADMIN')

router = Router()

cli = RedisHelper()


class Chat(StatesGroup):
    content = State()


class CustomContext(StatesGroup):
    content = State()


class DecissionChat(StatesGroup):
    content = State()


@router.message(CommandStart())
async def start_message(message: Message) -> None:
    orm.add_user(message.from_user.id)
    text = f'Привет {message.from_user.first_name}, я бот, который поможет тебе взаимодействовать с ChatGPT'
    await message.answer(text, reply_markup=MAIN_MENU)


@router.message(F.text == 'Новый чат - базовый контекст')
async def new_base_chat(message: Message, state: FSMContext) -> None:
    await state.set_state(Chat.content)
    cli.set(message.from_user.id, base_context)
    await message.answer(text='Погнали', reply_markup=END_CHAT)


@router.message(F.text == 'Новый чат - свой контекст')
async def custom_context(message: Message, state: FSMContext) -> None:
    await state.set_state(CustomContext.content)
    await message.answer('Какой контекст задать?')


@router.message(CustomContext.content)
async def new_base_chat(message: Message, state: FSMContext) -> None:
    await state.update_data(content=message.text)
    await state.set_state(Chat.content)
    cli.set(message.from_user.id, forming_message(role='system', text=message.text))
    await message.answer(text='Погнали', reply_markup=END_CHAT)


@router.message(F.text == 'Список сохранённых чатов')
async def get_list_contexts(message: Message):
    contexts = orm.get_list_contexts_by_user(message.from_user.id)
    if len(contexts) > 0:
        markup = forming_inline_lists(contexts)
        await message.answer(text='Вот список твоих контекстов', reply_markup=markup)
    else:
        await message.answer('У тебя нет сохранённых контекстов')


@router.callback_query()
async def choose_chat(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Chat.content)
    user_id = callback_query.from_user.id
    await callback_query.answer(callback_query.id)
    chat = orm.get_context(user_id, ctx_id=callback_query.data)
    cli.set(user_id, chat.content)
    cli.set(key=f'{user_id}_active', value=chat.name)
    await callback_query.answer(text=f'Погнали!', reply_markup=END_CHAT)


@router.message(Chat.content)
async def chating(message: Message, state: FSMContext):
    await state.update_data(content=message.text)
    user_id = message.from_user.id

    if message.text == 'Завершить чат':
        await message.answer(text='Сохранить текущую беседу или удалить?', reply_markup=ENDED_CHAT)
        await state.clear()
        await state.set_state(DecissionChat.content)

    elif message.text == 'Вытащи код':
        # Достаем из редиса последнее сообщение
        chat = cli.get(user_id)
        last_msg = chat[-1]
        just_code = extracting_code(last_msg['content'])

        chat.append(forming_message(role='assistant', text=just_code))
        cli.set(user_id, chat)

        await message.answer(text=just_code, reply_markup=CREATE_GISTS)
        await state.clear()
        await state.set_state(Chat.content)

    elif message.text == 'Создай gists':
        last_msg = cli.get(user_id)[-1]
        url = GistCreator(last_msg['content']).post()
        await message.answer(text=url, reply_markup=END_CHAT)
        await state.clear()
        await state.set_state(Chat.content)

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
        await state.clear()
        await state.set_state(Chat.content)


@router.message(DecissionChat.content)
async def decission_end_context(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name_chat = cli.get(f'{user_id}_active')
    if message.text == 'Сохранить':
        chat = cli.get(user_id)
        orm.save_context(user_id, name_chat, chat)
        cli.delete(user_id)
        cli.delete(f'{user_id}_active')
        await state.clear()
        await message.answer(text='Сохранил, можешь начать новый диалог', reply_markup=MAIN_MENU)
    elif message.text == 'Удалить':
        cli.delete(user_id)
        cli.delete(f'{user_id}_active')
        orm.delete_user_context(user_id, name_chat)
        await state.clear()
        await message.answer(text='Удалил, можешь начать новый диалог', reply_markup=MAIN_MENU)


async def main():
    bot = Bot(token=bot_token)

    @router.errors()
    async def error_handler(exception: ErrorEvent) -> None:
        await bot.send_message(
            chat_id=admin_id,
            text=f'Там всё упало - {type(exception).__name__}: {exception}'
        )

    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
