from aiogram import types

# Главное меню
MAIN_MENU = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
btn1 = types.KeyboardButton('Новый чат - базовый контекст')
btn2 = types.KeyboardButton('Новый чат - свой контекст')
btn3 = types.KeyboardButton('Список сохранённых чатов')
MAIN_MENU.add(btn1, btn2, btn3)

# Завершение чата
ENDED_CHAT = types.reply_keyboard.ReplyKeyboardMarkup(row_width=1)
btn1 = types.KeyboardButton('Сохранить')
btn2 = types.KeyboardButton('Удалить')
ENDED_CHAT.add(btn1, btn2)

# Завершить чат
END_CHAT = types.reply_keyboard.ReplyKeyboardMarkup(row_width=1)
btn1 = types.KeyboardButton('Завершить чат')
END_CHAT.add(btn1)
