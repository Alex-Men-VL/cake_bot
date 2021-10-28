from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from .app import dp, bot


class RegisterUser(StatesGroup):
    pd_approval = State()
    phone_number = State()
    address = State()


@dp.message_handler(commands=['start'], state='*')
async def send_help_message(message: types.Message):
    message_text = 'Написать приветственное сообщение\n' \
                   'Для начала ознакомьтесь с согласием на обработку ' \
                   'персональных данных.\nБез вашего согласия мы не сможем ' \
                   'принять ваш заказ.'
    markup = types.InlineKeyboardMarkup(row_width=2)
    agreement_button = types.InlineKeyboardButton('Согласен',
                                                  callback_data='Согласен')
    markup.add(agreement_button)

    await message.answer(message_text,
                         disable_notification=True,
                         reply_markup=markup)
    await RegisterUser.pd_approval.set()


@dp.callback_query_handler(
    lambda choice: choice.data == 'Согласен',
    state=RegisterUser.pd_approval
)
async def get_user_consent(callback_query: types.CallbackQuery):
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text='Согласен на обработку персональных данных',
        reply_markup=None
    )
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)
    button = types.KeyboardButton('Определить номер', request_contact=True)
    keyboard.add(button)
    await bot.send_message(
        callback_query.from_user.id,
        'Для дальнейшей работы с ботом нужно указать свой номер телефона.\n'
        'Нажмите на кнопку для автоматического определения или '
        'введите его в строку ввода.',
        disable_notification=True,
        reply_markup=keyboard
    )
    await RegisterUser.next()


@dp.message_handler(content_types=['contact'], state=RegisterUser.phone_number)
@dp.message_handler(state=RegisterUser.phone_number)
async def get_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as user:
        try:
            user['phone_number'] = message.contact.phone_number
        except AttributeError:
            user['phone_number'] = message.text
        user['first_name'] = message.from_user.first_name
        user['last_name'] = message.from_user.last_name

    await bot.send_message(message.chat.id,
                           'Введите адрес доставки',
                           disable_notification=True,
                           reply_markup=None)
    await RegisterUser.next()


@dp.message_handler(content_types=types.ContentTypes.TEXT,
                    state=RegisterUser.address)
async def get_address(message: types.Message, state: FSMContext):
    async with state.proxy() as user:
        user['data'] = message.text

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)
    keyboard.add('Собрать торт')
    await bot.send_message(
        message.chat.id,
        'Регистрация завершена.\nМожете перейти к заказу торта.',
        disable_notification=True,
        reply_markup=keyboard)
    await state.finish()
