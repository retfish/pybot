# -*- coding: utf-8 -*-

# board24_lg_ua
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup


import asyncio
import logging
import time
from datetime import datetime
import cryptography
import pymysql
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, callback_query, message, update
from aiogram.utils import executor
from aiogram.utils.markdown import text
from config import *


class DB:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306, user='localuser', passwd='fr6h',
                           db='bot1', use_unicode=1, charset='utf8')
        self.conn.autocommit(True)
        self.cursor = self.conn.cursor()
        self.cursor.execute('SET NAMES utf8;')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')

    def close(self):
        self.cursor.close()
        self.conn.close()

    def execute(self, sql, param):
        self.cursor.execute(sql, param)
        return True

    def execute_wo_param_one(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def execute_one(self, sql, param):
        self.cursor.execute(sql, param)
        return self.cursor.fetchone()

    def execute_all(self, sql, param):
        self.cursor.execute(sql, param)
        return self.cursor.fetchall()

    def proc_call(self, sql, param):
        self.cursor.callproc(sql, param)
        return True

    def rowcount(self, sql, param):
        self.cursor.execute(sql, param)
        return self.cursor.rowcount

    def last_row_wi(self, sql, param):
        self.cursor.execute(sql, param)
        return self.cursor.lastrowid


class SetStates(StatesGroup):
    timeFrom = State()
    timeTo = State()
    yway = State()
    setCity = State()
    addFilters = State()
    edit = State()
    qwe = State()
    rty = State()
    uio = State()
    pas = State()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
bot = Bot(token=TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

print(datetime.today())


def data_update(user_id):
    visit_date = datetime.today()
    db = DB()
    # logger.debug(VisitDate, user_id)
    db.execute("UPDATE board_sd_bot_user set LastVisit = %s WHERE Code = %s ", (visit_date, user_id))
    db.close()


# Start command

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    markup_zero = ReplyKeyboardMarkup(resize_keyboard=True) \
        .row(KeyboardButton("✅ Подписаться"), KeyboardButton("❎ Отписаться"), KeyboardButton("❓ Информация"),
             KeyboardButton('Настройки'))
    await message.reply("Привет! Я бот https://board24.lg.ua\n\nСейчас я умею:\n" +
                        "✅ Подписываться на оповещения о новых публикациях в избранных разделах;\n" +
                        "❎ Отписываться от ненужных.\n\n" +
                        "Выбирай нужное действие в меню",
                        reply_markup=markup_zero)
    data_update(message.from_user.id)


# Подписки\Отписки


@dp.message_handler(lambda message: message.text and 'писаться' in message.text.lower())
async def all_msg_handler(message: types.Message):
    button_text = message.text
    logger.debug('The answer is %r', button_text)  # print the text we've got
    logger.debug(
        message)  # {"message_id": 271, "from": {"id": 337835580, "is_bot": false, "first_name": "Dmitry", "language_code": "ru"}, "chat": {"id": 337835580, "first_name": "Dmitry", "type": "private"}, "date": 1614537085, "text": "✅ Подписаться"}
    if message.from_user.is_bot:
        return ()
    user_id = message.from_user.id
    data_update(user_id)
    db = DB()

    # ids = ''
    # userid = 0

    if db.rowcount("SELECT Id FROM board_sd_bot_user where Code=%s", user_id) > 0:
        row = db.execute_one("SELECT Id FROM board_sd_bot_user where Code=%s", user_id)
        userid = row[0]
    else:
        userid = 0

    # add new user(работает)
    if userid == 0 and button_text.find('Подписаться') > 0:
        firstname = message.from_user.first_name
        userid = db.last_row_wi("INSERT INTO board_sd_bot_user (Code,Name) VALUES (%s,%s)", (user_id, firstname))
        logger.debug('new userr id', userid)
    logger.debug('5')
    if userid == 0:
        return ()
    logger.debug(user_id)
    logger.debug(userid)
    if button_text.find('Подписаться') > 0:
        categories = db.execute_all("SELECT * FROM board_sd_category where Id not in " +
                       "(select CategoryId from board_sd_user_category where UserId='%s')", userid)
        keys = InlineKeyboardMarkup()
        for category in categories:
            cat = category[0]
            url = category[1]
            descr = category[2]
            # icon = category[3]
            # if len(icon) > 0:
            #    descr = icon + " " + descr
            #    logger.debug(icon)
            keys.row(InlineKeyboardButton(descr, callback_data='cat_in_' + str(cat)))
        await message.reply('✅ Подписаться', reply_markup=keys, reply=False)

    if button_text.find('Отписаться') > 0:
        categories = db.execute_all("SELECT * FROM board_sd_category where Id in " +
                       "(select CategoryId from board_sd_user_category where UserId='%s')", userid)
        keys = InlineKeyboardMarkup()
        for category in categories:
            cat = category[0]
            url = category[1]
            descr = category[2]
            """
            icon = category[3]
            if len(icon) > 0:
                descr = icon + " " + descr
            """
            keys.row(InlineKeyboardButton(descr, callback_data='cat_out_' + str(cat)))
        await message.reply('❎ Отписаться', reply_markup=keys, reply=False)

    db.close()


# Информация


@dp.message_handler(lambda message: message.text and 'информация' in message.text.lower())
async def info_msg_handler(message: types.Message):
    userid = message.from_user.id
    db = DB()
    alltime = db.execute_one("SELECT AllTime FROM board_sd_bot_user WHERE Code = %s", userid)
    if alltime[0] == 1:
        await message.reply('Уведомления будут приходить круглосуточно', reply=False)
    else:
        t_from = db.execute_one('SELECT TimeFrom FROM board_sd_bot_user WHERE Code = %s', userid)
        t_to = db.execute_one('SELECT TimeTo FROM board_sd_bot_user WHERE Code = %s', userid)
        print(t_to)
        print(t_from)
        await message.reply('Время оповещения с ' + str(t_from[0]) + ' до ' + str(t_to[0]), reply=False)
    db.close()


# Настройки


@dp.message_handler(lambda message: message.text and 'настройки' in message.text.lower())
async def settings_handler(message: types.Message):
    settings_keys = InlineKeyboardMarkup(row_width=1)
    settings_keys.add(InlineKeyboardButton('Время оповещений', callback_data='sets'),
                      InlineKeyboardButton('Установить время оповещения круглосуточно', callback_data='alltime'),
                      InlineKeyboardButton('Настроить фильтры', callback_data='f_sets'))
    await message.reply('Что настраиваем', reply_markup=settings_keys, reply=False)


# Категории для настройки


@dp.callback_query_handler(lambda atime: atime.data and atime.data.startswith('f_sets'))
async def f_sets_show_category(cbq: types.CallbackQuery):
    user_id = cbq.from_user.id
    db = DB()
    keys = InlineKeyboardMarkup(row_width=1)
    userid = db.execute_one("SELECT Id FROM board_sd_bot_user where Code=%s", user_id)
    userid = str(userid[0])
    # print(userid)
    categories = db.execute_all('SELECT CategoryId FROM board_sd_user_category WHERE UserId = %s', userid)
    for i in categories:
        categories_2 = db.execute_all('SELECT * FROM board_sd_category WHERE Id = %s', i[0])
        for i2 in categories_2:
            name = i2[2]
            cb_id = i[0]
            keys.row(InlineKeyboardButton(name,callback_data='f_sets' + str(cb_id) ))
    await bot.send_message(cbq.from_user.id, text='Выбрать категорию для настройки', reply_markup=keys)
    await bot.edit_message_text(
        text='Выберите категорию для настройки',
        chat_id=cbq.message.chat.id,
        message_id=cbq.message.message_id, )
    await SetStates.edit.set()
    db.close()


# Настройки категорий


@dp.callback_query_handler(lambda atime: atime.data and atime.data.startswith('f_sets'), state=SetStates.edit)
async def f_sets_cats(cbq: types.CallbackQuery, state: FSMContext):
    cat = str(cbq.data[6:])
    print(cat)
    kbd_for_set = InlineKeyboardMarkup(row_width=2)
    kbd_for_set.add(InlineKeyboardButton('Добавить список фильтров', callback_data='qwe_' + cat),
                    InlineKeyboardButton('Добавить город', callback_data='rty_' + cat),
                    InlineKeyboardButton('Убрать из списка фидьров', callback_data='uio_' + cat),
                    InlineKeyboardButton('Убрать город', callback_data='pas_' + cat))
    await bot.edit_message_text(
        text='Настраиваем..',
        chat_id=cbq.message.chat.id,
        message_id=cbq.message.message_id,
        reply_markup=kbd_for_set)
    await state.finish()

# Настройки категорий >>> Добавить список фильтров (qwe)


@dp.callback_query_handler(lambda c1: c1.data and c1.data.startswith('qwe_'))
async def test(cbq: types.CallbackQuery, state: FSMContext):
    cat = str(cbq.data[4:])
    db = DB()

    filters_list = db.execute_one('SELECT FiltersList FROM board_sd_user_category WHERE CategoryId = %s', cat)
    if filters_list[0] is None:
        str1 = 'Список пуст,введите слова через запятую'
    else:
        str1 = 'Текущий список: ' + filters_list[0] + '.Введите слова которые хотите добавить.'
    await bot.edit_message_text(
        text=str1,
        chat_id=cbq.message.chat.id,
        message_id=cbq.message.message_id)
    await SetStates.qwe.set()

    async with state.proxy() as data:
        data['qwe'] = cat
    db.close()


# Добавление списка фильров через настройки (qwe)


@dp.message_handler(state=SetStates.qwe)
async def qwe(msg: types.Message, state: FSMContext):
    acquired = msg.text.split(',')
    async with state.proxy() as data:
        cat = data['qwe']

    db = DB()
    current = db.execute_one('SELECT FiltersList FROM board_sd_user_category WHERE CategoryId = %s', cat)
    current = current[0]
    if current is not None:
        for i in acquired:
            if i not in current:
                current += ',' + i
        db.execute('UPDATE board_sd_user_category SET FiltersList = %s WHERE CategoryId = %s', (current, cat))
    else:
        s = ','.join(str(x) for x in acquired)
        db.execute('UPDATE board_sd_user_category SET FiltersList = %s WHERE CategoryId = %s', (s, cat))
    db.close()
    async with state.proxy() as data:
        data['qwe'] = None
    await state.finish()
    await bot.send_message(text='Фильтры добавлены.', chat_id=msg.from_user.id)


# Установка времени оповещений по умолчанию


@dp.callback_query_handler(lambda atime: atime.data and atime.data.startswith('alltime'))
async def set_default(cbq: types.CallbackQuery):
    userid = cbq.from_user.id
    db = DB()
    db.execute('UPDATE board_sd_bot_user SET AllTime = 1, TimeFrom = NULL, TimeTo = NULL WHERE Code = %s', userid)
    db.close()
    await bot.edit_message_text(
        text='Уведомления будут приходить круглосуточно',
        chat_id=cbq.message.chat.id,
        message_id=cbq.message.message_id, )

    await bot.answer_callback_query(cbq.id, text='')


# НАчало настройки времени оповещений


@dp.callback_query_handler(lambda cb: cb.data and cb.data.startswith('sets'))
async def t_from_set(cbq: types.CallbackQuery):
    await SetStates.timeFrom.set()
    await bot.send_message(cbq.from_user.id, 'Введите время начала,от 0 до 23')
    # cbq.message.chat.id
    await bot.edit_message_text(
        text='Настройки времени оповещений',
        chat_id=cbq.message.chat.id,
        message_id=cbq.message.message_id, )

    await bot.answer_callback_query(cbq.id, text='')


@dp.message_handler(
    lambda message1: not message1.text.isdigit() or message1.text.isdigit() and int(message1.text) not in range(0, 24),
    state=SetStates.timeFrom)
async def process_gender_invalid(msg: types.Message):
    return await msg.reply("Это не число,повторите ввод.")


@dp.message_handler(state=SetStates.timeFrom)
async def set_time_from(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['timeFrom'] = msg.text
    await SetStates.next()
    await msg.reply("Введите время окончания,с 1 до 24")


@dp.message_handler(lambda mess: not mess.text.isdigit() or mess.text.isdigit() and int(mess.text) not in range(1, 25),
                    state=SetStates.timeTo)
async def set_time_to(msg: types.Message, state: FSMContext):
    return await msg.reply('Неправильно,ещё раз')


# Последний шаг настройки времени оповещений


@dp.message_handler(state=SetStates.timeTo)
async def time_to_confirm(mess: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['timeTo'] = mess.text
    d1 = data['timeFrom']
    d2 = data['timeTo']
    if d2 <= d1:
        return await mess.reply('Неправильно,ещё раз')
    else:
        await bot.send_message(
            mess.chat.id, 'Закончили')
        await state.finish()
    user_id = mess.from_user.id
    logger.debug(d1)
    logger.debug(d2)
    logger.debug(user_id)
    db = DB()
    db.execute('UPDATE board_sd_bot_user SET TimeFrom = %s, TimeTo = %s, AllTime = 0 WHERE Code = %s', (d1, d2
                                                                                                            , user_id))
    db.close()


# Обработка подписки


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('cat_in_'))
async def process_callback_button_cat_i(callback_query: types.CallbackQuery):
    logger.debug(callback_query)
    code = callback_query.data[7:]
    user_code = callback_query.from_user.id
    data_update(user_code)
    logger.debug('Selected Code is %s',
                 code)  # {"id": "1450992769837060579", "from": {"id": 337835580, "is_bot": false, "first_name": "Dmitry", "language_code": "ru"}, "message": {"message_id": 266, "from": {"id": 1624821792, "is_bot": true, "first_name": "board24.lg.ua", "username": "board24_lg_ua_bot"}, "chat": {"id": 337835580, "first_name": "Dmitry", "type": "private"}, "date": 1614516496, "reply_to_message": {"message_id": 265, "from": {"id": 337835580, "is_bot": false, "first_name": "Dmitry", "language_code": "ru"}, "chat": {"id": 337835580, "first_name": "Dmitry", "type": "private"}, "date": 1614516496, "text": "✅ Подписаться"}, "text": "✅ Подписаться", "reply_markup": {"inline_keyboard": [[{"text": "🚛 Автотранспорт/продам/прицеп", "callback_data": "cat_in_01"}], [{"text": "🚗 Автотранспорт/продам/легковые иномарки", "callback_data": "cat_in_02"}], [{"text": "🏛 Недвижимость/продам/гаражи и прочее", "callback_data": "cat_in_03"}]]}}, "chat_instance": "5001750296641052025", "data": "cat_in_01"}
    if code.isdigit():
        code = int(code)
    successfully = True

    db = DB()
    if code in range(1, 5):
        db.proc_call('AddCategoryToUser', (user_code, code, 0))
        res = db.execute_wo_param_one('SELECT @_AddCategoryToUser_0, @_AddCategoryToUser_1, @_AddCategoryToUser_2')
        # logger.debug(res)
        if res[2] < 0:
            successfully = False
        await bot.answer_callback_query(callback_query.id, text='Подисываемся')
    else:
        await bot.send_message(text='Nope', chat_id=callback_query.from_user.id)
    db.close()
    ks = InlineKeyboardMarkup()
    ks.row(InlineKeyboardButton('Да', callback_data='Yes'),
           (InlineKeyboardButton('Нет', callback_data='No' + str(code))))

    if successfully:
        await bot.edit_message_text(
            text='Успешно подписались.Настроить фильтры?',
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=ks)

    else:
        await bot.edit_message_text(
            text='Уже подписались',
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id, )

        await bot.answer_callback_query(callback_query.id, text='')


# Добавление фильтров после подписки 1


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('Yes'))
async def yes_way(cbq: types.CallbackQuery):
    await SetStates.yway.set()
    await bot.send_message(cbq.from_user.id, 'Ввести список через запятую')
    await bot.edit_message_text(
        text='Список слов для отсеивания',
        chat_id=cbq.message.chat.id,
        message_id=cbq.message.message_id, )
    await bot.answer_callback_query(cbq.id, text='')


# Добавление фильтров после подписки 2


@dp.message_handler(state=SetStates.yway)
async def y_way(msg: types.Message, state: FSMContext):
    db = DB()
    user_id = msg.from_user.id
    user_code = db.execute_one('SELECT Id FROM board_sd_bot_user WHERE Code = %s', user_id)
    logger.debug(user_code[0])
    user_cat = db.execute_one('SELECT CategoryId FROM board_sd_user_category WHERE UserId = %s', user_code[0])
    f_list = msg.text.split()
    cur_fltrs_lst = db.execute_one('SELECT FiltersList FROM board_sd_user_category WHERE UserId = %s', user_cat[0])
    if cur_fltrs_lst is None:
        print('1')
        for i in f_list:
            db.execute('UPDATE board_sd_user_category SET FiltersList = %s WHERE UserId = %s AND CategoryId = %s',
                           (i, user_code[0], user_cat[0]))
    else:
        print('2')
        for i2 in f_list:
            i2 += cur_fltrs_lst
            db.execute('UPDATE board_sd_user_category SET FiltersList = %s WHERE UserId = %s AND CategoryId = %s',
                           (i2, user_code[0], user_cat[0]))
    """
    for i in f_list:
        cursor.execute('UPDATE board_sd_user_category SET FiltersList = %s WHERE UserId = %s AND CategoryId = %s',
                       (i, user_code[0], user_cat[0]))
    
    for i in f_list:
        cursor.execute('INSERT IGNORE INTO board_sd_user_category(UserId, CategoryId, FiltersList) VALUES (%s, %s , %s)',
                       (user_code[0], user_cat[0], i))
    """
    db.close()
    await state.finish()

    kbd = InlineKeyboardMarkup()
    kbd.row(InlineKeyboardButton('Да', callback_data='city_y', ),
            InlineKeyboardButton('Нет', callback_data='city_n'))
    await bot.send_message(text='Фильтры добавлены,теперь выберем город?', chat_id=msg.from_user.id, reply_markup=kbd)

    # print(f_list)

    pass


# Отказ от настройки фильтров после подписки (done)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('No'))  # done
async def no_way(cbq: types.CallbackQuery):
    cat = str(cbq.data[2:])
    kbd = InlineKeyboardMarkup()
    kbd.row(InlineKeyboardButton('Да', callback_data='city_y' + cat ),
            InlineKeyboardButton('Нет', callback_data='city_n' + cat))
    await bot.edit_message_text(text='Настроить фильтры всегда можно в настройках,а теперь выберем город?',
                                chat_id=cbq.message.chat.id,
                                message_id=cbq.message.message_id, reply_markup=kbd)

# Отказ от выбора города при подписке (done)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('city_n'))
async def city_no(cbq: types.CallbackQuery):
    print(cbq.data)
    # s = 'Лисичанск,Северодонецк,Рубежное'
    s = ','.join(str(x) for x in city_list_const)
    db= DB()

    user_id = cbq.from_user.id
    user_code = db.execute_one('SELECT Id FROM board_sd_bot_user WHERE Code = %s', user_id)
    logger.debug(user_code[0])

    user_cat = str(cbq.data[6:])

    db.execute('UPDATE board_sd_user_category SET CityList = %s WHERE UserId = %s AND CategoryId = %s', (s,
                                                                                                             user_code[
                                                                                                                 0],
                                                                                                             user_cat
                                                                                                                 ))
    db.close()
    print(user_code[0])
    print(user_cat[0])
    await bot.edit_message_text(text='блалала',
                                chat_id=cbq.message.chat.id,
                                message_id=cbq.message.message_id)

# Кнопки для ывбора города при подписке (done)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('city_y'))
async def city_yes(cbq: types.CallbackQuery):
    cat = str(cbq.data[6:])
    print(cbq.data)
    # s = 'Лисичанск,Северодонецк,Рубежное'
    s = ','.join(str(x) for x in city_list_const) # https://stackoverflow.com/questions/497765/python-string-joinlist-on-object-array-rather-than-string-array
    kbd = InlineKeyboardMarkup()
    for i in s.split(','):
        kbd.row(InlineKeyboardButton(i, callback_data='ssq' + str(i) + cat))
        await bot.edit_message_text(text='блалала2',
                                    chat_id=cbq.message.chat.id,
                                    message_id=cbq.message.message_id,
                                    reply_markup=kbd)

# Внесение города в базу (done)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('ssq'))
async def city_yes_yes(cbq: types.CallbackQuery):
    city = str(cbq.data[3:-1])
    cat = str(cbq.data[-1])
    print('588 ', city , cat)
    db = DB()
    user_id = cbq.from_user.id
    user_code = db.execute_one('SELECT Id FROM board_sd_bot_user WHERE Code = %s', user_id)
    uid = int(user_code[0])
    logger.debug(uid)
    curent = db.execute_one('SELECT CityList FROM board_sd_user_category WHERE UserId = %s AND CategoryId = %s', (uid,
                                                                                                         cat))
    if curent[0] is not None:
        city_str = str(curent[0])
        city_list = city_str.split(',')
        if city not in city_list:
            city_str += ',' + city
            print(city_str + '1')
    else:
        city_str = city
        print(city_str + '2')
    db.execute('UPDATE board_sd_user_category SET CityList = %s WHERE UserId = %s AND CategoryId = %s', (city_str,
                                                                                                             uid,
                                                                                                             cat))
    await bot.edit_message_text(text='Город добавен',
                                chat_id=cbq.message.chat.id,
                                message_id=cbq.message.message_id)
    db.close()
    pass


# Обработка отписки

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('cat_out_'))
async def process_callback_button_cat_i(callback_query: types.CallbackQuery):
    code = callback_query.data[8:]
    user_code = callback_query.from_user.id
    data_update(user_code)
    logger.debug('Selected Code is %s', code)
    if code.isdigit():
        code = int(code)
    successfully = True

    db = DB()
    if code in range(1, 5):
        res = db.execute_one('SELECT Id FROM board_sd_bot_user WHERE Code = %s', user_code)
        user_id = res[0]
        print('613', res)
        res = db.rowcount('DELETE FROM board_sd_user_category WHERE UserId = %s and CategoryId = %s', (user_id, code))
        if res <= 0:
            successfully = False
        await bot.answer_callback_query(callback_query.id, text='Отписываемся')
    else:
        await bot.send_message(text='Nope', chat_id=callback_query.from_user.id)
    db.close()

    if successfully:
        await bot.edit_message_text(
            text='Отписались',
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id, )

        await bot.answer_callback_query(callback_query.id, text='')
    else:
        await bot.edit_message_text(
            text='ОТписались ещё раз',
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id, )

        await bot.answer_callback_query(callback_query.id, text='')


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
    data_update(message.from_user.id)


# print(get_all_times(579198619))

if __name__ == '__main__':
    print('start', time.ctime())

    loop = asyncio.get_event_loop()
    print('run bot', time.ctime())
    executor.start_polling(dp)
    print('end bot', time.ctime())
    loop.run_forever()

    print('stop', time.ctime())
