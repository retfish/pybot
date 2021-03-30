# -*- coding: utf-8 -*-

# board24_lg_ua

import logging

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.markdown import text
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, callback_query

# from config import TOKEN
# import keyboards as kb

import pymysql

import time
import asyncio

# from bs4 import BeautifulSoup
# import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TOKEN = '1743194367:AAGT1halXXTf-i7UG7-XCUkEDT0SOZ6vz5g'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

print(datetime.today())
# Start command

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    markup_zero = ReplyKeyboardMarkup(resize_keyboard=True) \
        .row(KeyboardButton("✅ Подписаться"), KeyboardButton("❎ Отписаться"), KeyboardButton("❓ Информация"))
    await message.reply("Привет! Я бот https://board24.lg.ua\n\nСейчас я умею:\n" +
                        "✅ Подписываться на оповещения о новых публикациях в избранных разделах;\n" +
                        "❎ Отписываться от ненужных.\n\n" +
                        "Выбирай нужное действие в меню",
                        reply_markup=markup_zero)
    VisitDate = datetime.today()
    user_id = message.from_user.id
    conn = pymysql.connect(host='a120c.mysql.ukraine.com.ua', port=3306, user='a120c_dwk', passwd='1qaZXdr5',
                           db='a120c_dwk', use_unicode=1, charset='utf8')
    conn.autocommit(True)

    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    cursor.execute("INSERT INTO board_sd_bot_user (LastVisit) VALUE (%s)",VisitDate)

    cursor.close()
    conn.close()


@dp.message_handler(lambda message: message.text and 'писаться' in message.text.lower())
async def all_msg_handler(message: types.Message):
    button_text = message.text
    logger.debug('The answer is %r', button_text)  # print the text we've got
    logger.debug(
        message)  # {"message_id": 271, "from": {"id": 337835580, "is_bot": false, "first_name": "Dmitry", "language_code": "ru"}, "chat": {"id": 337835580, "first_name": "Dmitry", "type": "private"}, "date": 1614537085, "text": "✅ Подписаться"}
    if message.from_user.is_bot:
        return ()
    user_id = message.from_user.id
    # logger.debug(user_id)

    conn = pymysql.connect(host='a120c.mysql.ukraine.com.ua', port=3306, user='a120c_dwk', passwd='1qaZXdr5',
                           db='a120c_dwk', use_unicode=1, charset='utf8')
    conn.autocommit(True)

    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    # ids = ''
    userid = 0

    cursor.execute("SELECT Id FROM board_sd_bot_user where Code=%s", user_id)
    if cursor.rowcount > 0:
        row = cursor.fetchone()
        userid = row[0]
        # logger.debug(userid)

    # add new user
    if userid == 0 & button_text.find('Подписаться') > 0:
        firstname = message.from_user.first_name
        cursor.execute("INSERT INTO board_sd_bot_user (Code,Name) VALUES (%s,%s)", (user_id, firstname))
        # cursor.execute("INSERT INTO board_sd_bot_user (Code,Name) VALUES ("+user_id+","+message.from_user.first_name+")")
        userid = cursor.lastrowid
    if userid == 0:
        return ()
    if button_text.find('Подписаться') > 0:
        cursor.execute("SELECT * FROM board_sd_category where Id not in " +
                       "(select CategoryId from board_sd_user_category where UserId='%s')", userid)
        keys = InlineKeyboardMarkup()
        categories = cursor.fetchall()
        for category in categories:
            cat = category[0]
            url = category[1]
            descr = category[2]
            # icon = category[3]
            # if len(icon) > 0:
            #    descr = icon + " " + descr
            #    logger.debug(icon)
            keys.row(InlineKeyboardButton(descr, callback_data='cat_in_0' + str(cat)))
        await message.reply('✅ Подписаться', reply_markup=keys)
    if button_text.find('Отписаться') > 0:
        cursor.execute("SELECT * FROM board_sd_category where Id in " +
                       "(select CategoryId from board_sd_user_category where UserId='%s')", userid)
        keys = InlineKeyboardMarkup()
        categories = cursor.fetchall()
        for category in categories:
            cat = category[0]
            url = category[1]
            descr = category[2]
            icon = category[3]
            if len(icon) > 0:
                descr = icon + " " + descr
            keys.row(InlineKeyboardButton(descr, callback_data='cat_out_0' + str(cat)))
        await message.reply('❎ Отписаться', reply_markup=keys)

    if button_text.find('Информация') > 0:
        await bot.answer_callback_query(callback_query.id, text='Подисываемся')

    cursor.close()
    conn.close()


# Обработка подписки


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('cat_in_'))
async def process_callback_button_cat_i(callback_query: types.CallbackQuery):
    logger.debug(callback_query)
    code = callback_query.data[-2:]
    user_code = callback_query.from_user.id
    logger.debug('Selected Code is %s',
                 code)  # {"id": "1450992769837060579", "from": {"id": 337835580, "is_bot": false, "first_name": "Dmitry", "language_code": "ru"}, "message": {"message_id": 266, "from": {"id": 1624821792, "is_bot": true, "first_name": "board24.lg.ua", "username": "board24_lg_ua_bot"}, "chat": {"id": 337835580, "first_name": "Dmitry", "type": "private"}, "date": 1614516496, "reply_to_message": {"message_id": 265, "from": {"id": 337835580, "is_bot": false, "first_name": "Dmitry", "language_code": "ru"}, "chat": {"id": 337835580, "first_name": "Dmitry", "type": "private"}, "date": 1614516496, "text": "✅ Подписаться"}, "text": "✅ Подписаться", "reply_markup": {"inline_keyboard": [[{"text": "🚛 Автотранспорт/продам/прицеп", "callback_data": "cat_in_01"}], [{"text": "🚗 Автотранспорт/продам/легковые иномарки", "callback_data": "cat_in_02"}], [{"text": "🏛 Недвижимость/продам/гаражи и прочее", "callback_data": "cat_in_03"}]]}}, "chat_instance": "5001750296641052025", "data": "cat_in_01"}
    if code.isdigit():
        code = int(code)
    successfully = True

    conn = pymysql.connect(host='a120c.mysql.ukraine.com.ua', port=3306, user='a120c_dwk', passwd='1qaZXdr5',
                           db='a120c_dwk', use_unicode=1, charset='utf8')
    conn.autocommit(True)

    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    if code == 1:
        cursor.callproc('AddCategoryToUser', (user_code, code, 0))
        cursor.execute('SELECT @_AddCategoryToUser_0, @_AddCategoryToUser_1, @_AddCategoryToUser_2')
        res = cursor.fetchone()
        # logger.debug(res)
        if res[2] < 0:
            successfully = False
        await bot.answer_callback_query(callback_query.id, text='Подисываемся')
    if code == 2:
        cursor.callproc('AddCategoryToUser', (user_code, code, 0))
        cursor.execute('SELECT @_AddCategoryToUser_0, @_AddCategoryToUser_1, @_AddCategoryToUser_2')
        res = cursor.fetchone()
        if res[2] < 0:
            successfully = False
        await bot.answer_callback_query(callback_query.id, text='Подисываемся')
    if code == 3:
        cursor.callproc('AddCategoryToUser', (user_code, code, 0))
        cursor.execute('SELECT @_AddCategoryToUser_0, @_AddCategoryToUser_1, @_AddCategoryToUser_2')
        res = cursor.fetchone()
        if res[2] < 0:
            successfully = False
        await bot.answer_callback_query(callback_query.id, text='Подисываемся')

    cursor.close()
    conn.close()

    if successfully:
        await bot.send_message(callback_query.from_user.id, 'Подписка оформлено успешно')
    else:
        await bot.send_message(callback_query.from_user.id, 'Подписка уже оформлена')


# Обработка отписки


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('cat_out_'))
async def process_callback_button_cat_i(callback_query: types.CallbackQuery):
    code = callback_query.data[-2:]
    user_code = callback_query.from_user.id
    logger.debug('Selected Code is %s', code)
    if code.isdigit():
        code = int(code)
    successfully = True

    conn = pymysql.connect(host='a120c.mysql.ukraine.com.ua', port=3306, user='a120c_dwk', passwd='1qaZXdr5',
                           db='a120c_dwk', use_unicode=1, charset='utf8')
    conn.autocommit(True)

    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    if code == 1:
        cursor.callproc('DeleteCategoryToUser', (user_code, code, 0))
        cursor.execute('SELECT @_DeleteCategoryToUser_0, @_DeleteCategoryToUser_1, @_DeleteCategoryToUser_2')
        res = cursor.fetchone()
        if res[2] < 0:
            successfully = False
        await bot.answer_callback_query(callback_query.id, text='Отписываемся')
    if code == 2:
        cursor.callproc('DeleteCategoryToUser', (user_code, code, 0))
        cursor.execute('SELECT @_DeleteCategoryToUser_0, @_DeleteCategoryToUser_1, @_DeleteCategoryToUser_2')
        res = cursor.fetchone()
        if res[2] < 0:
            successfully = False
        await bot.answer_callback_query(callback_query.id, text='Отписываемся')
    if code == 3:
        cursor.callproc('DeleteCategoryToUser', (user_code, code, 0))
        cursor.execute('SELECT @_DeleteCategoryToUser_0, @_DeleteCategoryToUser_1, @_DeleteCategoryToUser_2')
        res = cursor.fetchone()
        if res[2] < 0:
            successfully = False
        await bot.answer_callback_query(callback_query.id, text='Отписываемся')

    cursor.close()
    conn.close()

    if successfully:
        await bot.send_message(callback_query.from_user.id, 'Успешно отписались')
    else:
        await bot.send_message(callback_query.from_user.id, 'Уже отписались ранее')


##


help_message = text(
    "Привет я бот https://board24.lg.ua",
    "\nСейчас я умею:",
    "✅ Подписываться на оповещения о нывых публикациях в избранных разделах",
    "❎ Отписываться",
    sep="\n"
)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(help_message)


if __name__ == '__main__':
    print('start', time.ctime())

    loop = asyncio.get_event_loop()
    print('run bot', time.ctime())
    executor.start_polling(dp)
    print('end bot', time.ctime())
    loop.run_forever()

    print('stop', time.ctime())
