import logging
import asyncio

from aiogram import Bot,types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from config import TOKEN
#from aiogram.utils.emoji import emojize
#from aiogram.types.message import ContentType
from aiogram.utils.markdown import text,bold,code,pre
from aiogram.types import ParseMode,InputMediaPhoto,InputMediaAudio,ChatActions,InputMediaVideo


CAT_BIG_EYES = 'AgADAgADNqkxG3hu6Eov3mINslrI7jUWnA4ABAX7PAfFIfbONj0AAgI'
KITTENS = [
    'AgADAgADN6kxG3hu6EqJjqtjb2_dtnztAw4ABMPliaCdHTFDDxsCAAEC',
    'AgADAgADNakxG3hu6Epaq9GtKVQcmEPqAw4ABKKK02zsSoEJtRwCAAEC',
    'AgADAgADNKkxG3hu6EoNC-hZek5IUkeZQw4ABPbUDtX7JTIZmjwAAgI',
]
VOICE = 'AwADAgADXQEAAnhu6EqAvqdylJRvBgI'
VIDEO = 'BAADAgADXAEAAnhu6ErDHE-xNjIzMgI'
TEXT_FILE = 'BQADAgADWgEAAnhu6ErgyjSYkwOL6AI'
VIDEO_NOTE = 'DQADAgADWwEAAnhu6EoFqDa-fStSmgI'


bot = Bot(token = TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def procces_start_command(message: types.Message):
    await message.reply("Привет")

@dp.message_handler(commands=['help'])
async def procces_help_command(message: types.Message):
    msg = text(bold('Я могу ответить на следующие команды:'),
               '/voice', '/photo', '/group', '/note', '/file, /testpre', sep='\n')
    await message.reply(msg,parse_mode=ParseMode.MARKDOWN)

@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id,msg.text)

@dp.message_handler(commands=['voice'])
async def procces_voice_command(message:types.Message):
    await bot.send_voice(message.from_user.id,VOICE,
                         reply_to_message_id=message.message_id)

if __name__ == '__main__':
    executor.start_polling(dp)




