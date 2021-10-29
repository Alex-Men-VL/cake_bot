from aiogram import types
from aiogram.dispatcher import FSMContext

from .cake_parameters import DECORS
from ..app import bot


def get_markup(parameters):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for parameter in parameters:
        button = types.InlineKeyboardButton(parameter,
                                            callback_data=parameter.split()[0])
        markup.add(button)
    return markup


def get_one_button_markup(text):
    markup = types.InlineKeyboardMarkup()
    continue_button = types.InlineKeyboardButton(text,
                                                 callback_data=text)
    markup.add(continue_button)
    return markup


async def send_message_with_decors(chat_id):
    markup = get_markup(DECORS)
    continue_button = types.InlineKeyboardButton('Без декора',
                                                 callback_data='Без декора')
    markup.add(continue_button)
    await bot.send_message(chat_id,
                           'Добавьте декор по желанию',
                           disable_notification=True,
                           reply_markup=markup)


async def send_message_with_title(chat_id, state: FSMContext):
    markup = get_one_button_markup('Без надписи')
    message = await bot.send_message(
        chat_id,
        'Добавьте надпись к торту по желанию (+ 500).\n'
        'Мы можем разместить на торте любую надпись, '
        'например: «С днем рождения!»\nОтправьте боту желаемую фразу в виде '
        'сообщения или нажмите на кнопку «Без надписи»',
        disable_notification=True,
        reply_markup=markup
    )
    async with state.proxy() as cake:
        cake['title_message_id'] = message.message_id


async def send_message_with_comment(chat_id, state: FSMContext):
    markup = get_one_button_markup('Без комментария')
    message = await bot.send_message(
        chat_id,
        'Добавьте комментарий к заказу.',
        disable_notification=True,
        reply_markup=markup
    )
    async with state.proxy() as cake:
        cake['comment_message_id'] = message.message_id


async def send_message_with_address(chat_id, state: FSMContext):
    markup = get_one_button_markup('Доставить по этому адресу')
    address_from_bd = 'СПБ'
    message = await bot.send_message(
        chat_id,
        f'Доставить заказ по адресу:\n{address_from_bd}\nИли напишите новый '
        'адрес доставки.',
        disable_notification=True,
        reply_markup=markup
    )
    async with state.proxy() as cake:
        cake['address_message_id'] = message.message_id
        cake['address'] = address_from_bd


async def send_message_with_date(chat_id, state: FSMContext):
    message = await bot.send_message(
        chat_id,
        'Введите дату доставки',
        disable_notification=True,
        reply_markup=None
    )
    async with state.proxy() as cake:
        cake['date_message_id'] = message.message_id


async def finish_cake_collecting(chat_id, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                         resize_keyboard=True,
                                         row_width=2)
    keyboard.add('Заказать торт', 'Собрать торт заново', 'Главное меню')
    price = 1000
    await bot.send_message(chat_id,
                           f'Итоговая цена заказа: {price} р.',
                           disable_notification=True,
                           reply_markup=keyboard)
    await state.finish()
