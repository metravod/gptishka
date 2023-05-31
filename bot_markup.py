from typing import List

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.models import UserContext

# Главное меню
MAIN_MENU = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
btn1 = types.KeyboardButton('Новый чат - базовый контекст')
btn2 = types.KeyboardButton('Новый чат - свой контекст')
btn3 = types.KeyboardButton('Список сохранённых чатов')
MAIN_MENU.add(btn1, btn2, btn3)

# Завершение чата
ENDED_CHAT = types.reply_keyboard.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
btn1 = types.KeyboardButton('Сохранить')
btn2 = types.KeyboardButton('Удалить')
ENDED_CHAT.add(btn1, btn2)

# Завершить чат
END_CHAT = types.reply_keyboard.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
btn1 = types.KeyboardButton('Завершить чат')
END_CHAT.add(btn1)


# Фукнция для формирования inline клавиатуры со списком контекстов
def forming_inline_lists(contexts: dict) -> InlineKeyboardMarkup:
    inline_list = InlineKeyboardMarkup()
    for ctx_id, context in contexts.items():
        inline_list.add(InlineKeyboardButton(context, callback_data=ctx_id))
    return inline_list
