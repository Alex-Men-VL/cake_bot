import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv


load_dotenv()

bot = Bot(token=os.getenv('TG_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())
