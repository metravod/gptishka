from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

# Главное меню
MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Новый чат - базовый контекст'),
            KeyboardButton(text='Новый чат - свой контекст')
        ],
        [
            KeyboardButton(text='Список сохранённых чатов')
        ]
    ],
    row_width=2,
    resize_keyboard=True
)

# Завершение чата
ENDED_CHAT = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Сохранить'),
            KeyboardButton(text='Удалить')
        ]
    ],
    row_width=1,
    resize_keyboard=True
)

# Завершить чат
END_CHAT = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Завершить чат')]
    ],
    row_width=1,
    resize_keyboard=True
)

# Вытащить код
EXTRACT_CODE = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Вытащи код')]
    ],
    row_width=1,
    resize_keyboard=True
)

# Создать gists
CREATE_GISTS = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Создай gists')]
    ],
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
