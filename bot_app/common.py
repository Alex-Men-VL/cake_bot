from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from .app import dp
from .registration import RegisterUser
from .create_cake import CreateCake


@dp.message_handler(commands=['start'], state='*')
async def send_start_message(message: types.Message):
    message_text = 'Привет! Я помогу тебе заказать торт на любой вкус.\n'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=True)
    user_registered = False
    if user_registered:
        message_text += 'Вы уже зарегистрированы в системе. Можете перейти к ' \
                        'заказу торта.'
        markup.add('Собрать торт', 'Главное меню')
    else:
        message_text += 'Для начала зарегистрируйтесь в системе.'
        markup.add('Зарегистрироваться')
        await RegisterUser.start_registration.set()

    await message.answer(message_text,
                         disable_notification=True,
                         reply_markup=markup)


@dp.message_handler(Text(equals='Главное меню'), state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()

    keyboard = types.ReplyKeyboardMarkup(row_width=2,
                                         resize_keyboard=True,
                                         one_time_keyboard=True)
    keyboard.add('Собрать торт')
    user_has_orders = False
    if user_has_orders:
        keyboard.insert('Мои заказы')
    keyboard.insert('Главное меню')

    await message.answer('Вы перемещены в главное меню.\n',
                         reply_markup=keyboard)


@dp.message_handler(state='*')
async def send_help_message(message: types.Message):
    photo = open('././static/helper.jpeg', 'rb')
    text = 'Я тебя не понимаю.\n\nПожалуйста, воспользуйтесь кнопками в ' \
           'нижнем меню. Если у вас они не отображаются, просто нажмите на ' \
           'эту кнопку в поле ввода.'
    await message.answer_photo(photo, caption=text)

