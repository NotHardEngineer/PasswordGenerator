import string
import random

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config

inline_kb_settings = InlineKeyboardMarkup(row_width=2)
inline_btn_digits = InlineKeyboardButton(r"Включить\выключить цифры", callback_data='change_digit')
inline_btn_leters = InlineKeyboardButton(r"Включить\выключить буквы", callback_data='change_leters')
inline_btn_spec = InlineKeyboardButton(r"Включить\выключить спецсимволы", callback_data='change_spec')
inline_kb_settings.add(inline_btn_digits, inline_btn_leters, inline_btn_spec)

TOKEN = config.token


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

digits = [str(i) for i in range(0, 10)]
leters = list(string.ascii_lowercase)
specsyms = list(string.punctuation)


class PasswordGenerator:

    def __init__(self, userid):
        self.userid = userid
        self.usedigits = True
        self.useleters = True
        self.usespec = True

    def generate(self, length: int):
        password = ''
        symtypes = []
        if self.usedigits:
            symtypes.append(0)
        if self.useleters:
            symtypes.append(1)
        if self.usespec:
            symtypes.append(2)
        if len(symtypes) > 0:
            for i in range(length):
                symtype = symtypes[random.randint(0, len(symtypes) - 1)]
                if symtype == 0:
                    password = password + digits[random.randint(0, len(digits) - 1)]
                elif symtype == 1:
                    password = password + leters[random.randint(0, len(leters) - 1)]
                elif symtype == 2:
                    password = password + specsyms[random.randint(0, len(specsyms) - 1)]
            return password
        else:
            return ""


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('change'))
async def process_callback(callback_query: types.CallbackQuery):
    code = callback_query.data[7:]
    if code == 'digit':
        globals()['GeneratorObject_' + str(callback_query.from_user.id)].usedigits = \
            not globals()['GeneratorObject_' + str(callback_query.from_user.id)].usedigits
        if globals()['GeneratorObject_' + str(callback_query.from_user.id)].usedigits:
            await bot.answer_callback_query(callback_query.id, "Цифры будут появляться в пароле")
        else:
            await bot.answer_callback_query(callback_query.id, "Цифры не будут появляться в пароле")
    elif code == 'leters':
        globals()['GeneratorObject_' + str(callback_query.from_user.id)].useleters = \
            not globals()['GeneratorObject_' + str(callback_query.from_user.id)].useleters
        if globals()['GeneratorObject_' + str(callback_query.from_user.id)].useleters:
            await bot.answer_callback_query(callback_query.id, "Буквы будут появляться в пароле")
        else:
            await bot.answer_callback_query(callback_query.id, "Буквы не будут появляться в пароле")
    elif code == 'spec':
        globals()['GeneratorObject_' + str(callback_query.from_user.id)].usespec = \
            not globals()['GeneratorObject_' + str(callback_query.from_user.id)].usespec
        if globals()['GeneratorObject_' + str(callback_query.from_user.id)].usespec:
            await bot.answer_callback_query(callback_query.id, "Спецсимволы будут появляться в пароле")
        else:
            await bot.answer_callback_query(callback_query.id, "Спецсимволы не будут появляться в пароле")


@dp.message_handler(commands=['stop'])
async def process_stop_command(message: types.Message):
    del globals()['GeneratorObject_' + str(message.from_user.id)]
    await bot.send_message(message.from_user.id, r"Спасибо за использование бота, напиши /start для нового пароля")


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    globals()['GeneratorObject_' + str(message.from_user.id)] = PasswordGenerator(message.from_user.id)
    await bot.send_message(message.from_user.id, "Привет!\nС помощью кнопок настрой пароль и напиши мне желаемую "
                                                 "длинну пароля.", reply_markup=inline_kb_settings)


@dp.message_handler()
async def password_message(message: types.Message):
    try:
        to_send = globals()['GeneratorObject_' + str(message.from_user.id)].generate(int(message.text))
        if len(to_send) > 0:
            await process_stop_command(message)
        else:
            to_send = "Включи хотя бы один тип символов"
        await bot.send_message(message.from_user.id, to_send)
    except ValueError:
        to_send = "Отправь число!"
        await bot.send_message(message.from_user.id, to_send)
    except KeyError:
        await process_start_command(message)


if __name__ == '__main__':
    executor.start_polling(dp)
