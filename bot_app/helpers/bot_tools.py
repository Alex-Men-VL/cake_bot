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
    markup = types.InlineKeyboardMarkup()
    continue_button = types.InlineKeyboardButton('Без надписи',
                                                 callback_data='Без надписи')
    markup.add(continue_button)
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
