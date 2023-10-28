from dataclasses import dataclass

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)


@dataclass
class Buttons:
    base_context = KeyboardButton(text='Новый чат - базовый контекст')
    custom_context = KeyboardButton(text='Новый чат - свой контекст')
    list_saved_contexts = KeyboardButton(text='Список сохранённых чатов')
    save = KeyboardButton(text='Сохранить')
    delete = KeyboardButton(text='Удалить')
    end_chat = KeyboardButton(text='Завершить чат')
    extract_code = KeyboardButton(text='Вытащи код')
    create_gists = KeyboardButton(text='Создай gists')


# Главное меню
MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [Buttons.base_context, Buttons.custom_context],
        [Buttons.list_saved_contexts]
    ],
    row_width=2,
    resize_keyboard=True
)

# Завершение чата
ENDED_CHAT = ReplyKeyboardMarkup(
    keyboard=[[Buttons.save, Buttons.delete]],
    row_width=1,
    resize_keyboard=True
)

# Завершить чат
END_CHAT = ReplyKeyboardMarkup(
    keyboard=[[Buttons.end_chat]],
    row_width=1,
    resize_keyboard=True
)

# Вытащить код
EXTRACT_CODE = ReplyKeyboardMarkup(
    keyboard=[[Buttons.extract_code], [Buttons.end_chat]],
    row_width=1,
    resize_keyboard=True
)

# Создать gists
CREATE_GISTS = ReplyKeyboardMarkup(
    keyboard=[[Buttons.create_gists], [Buttons.end_chat]],
    row_width=1,
    resize_keyboard=True
)


# Фукнция для формирования inline клавиатуры со списком контекстов
def forming_inline_lists(contexts: dict) -> InlineKeyboardMarkup:
    keybord_list = [
        InlineKeyboardButton(text=context, callback_data=ctx_id)
        for ctx_id, context
        in contexts.items()
    ]
    inline_list = InlineKeyboardMarkup(inline_keyboard=[keybord_list])
    return inline_list
