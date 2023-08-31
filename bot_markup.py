from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
MAIN_MENU = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
new_base_chat = types.KeyboardButton('Новый чат - базовый контекст')
new_custom_chat = types.KeyboardButton('Новый чат - свой контекст')
show_all_my_chats = types.KeyboardButton('Список сохранённых чатов')
MAIN_MENU.add(new_base_chat, new_custom_chat, show_all_my_chats)

# Завершение чата
ENDED_CHAT = types.reply_keyboard.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
save_btn = types.KeyboardButton('Сохранить')
del_btn = types.KeyboardButton('Удалить')
ENDED_CHAT.add(save_btn, del_btn)

# Завершить чат
END_CHAT = types.reply_keyboard.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
end_btn = types.KeyboardButton('Завершить чат')
END_CHAT.add(end_btn)

# Вытащить код
EXTRACT_CODE = types.reply_keyboard.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
extract_btn = types.KeyboardButton('Вытащи код')
EXTRACT_CODE.add(extract_btn, end_btn)

# Создать gists
CREATE_GISTS = types.reply_keyboard.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
create_btn = types.KeyboardButton('Создай gists')
CREATE_GISTS.add(create_btn, end_btn)


# Фукнция для формирования inline клавиатуры со списком контекстов
def forming_inline_lists(contexts: dict) -> InlineKeyboardMarkup:
    inline_list = InlineKeyboardMarkup()
    for ctx_id, context in contexts.items():
        inline_list.add(InlineKeyboardButton(context, callback_data=ctx_id))
    return inline_list
