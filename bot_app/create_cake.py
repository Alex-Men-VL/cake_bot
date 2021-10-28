from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from .app import dp, bot
from .helpers import LEVELS, SHAPES, TOPPINGS, BERRIES, DECORS
from .helpers import get_markup, send_message_with_decors, \
    send_message_with_title


class CreateCake(StatesGroup):
    levels_number = State()
    shape = State()
    topping = State()
    berries = State()
    decor = State()
    title = State()


@dp.message_handler(Text(equals='Собрать торт'), state='*')
@dp.message_handler(Text(equals='Собрать торт заново'), state='*')
async def start_cake_collecting(message: types.Message):
    markup = get_markup(LEVELS)
    await message.answer('Выберите количество уровней',
                         disable_notification=True,
                         reply_markup=markup)
    await CreateCake.levels_number.set()


@dp.callback_query_handler(
    lambda choice: choice.data in [level.split()[0] for level in LEVELS],
    state=CreateCake.levels_number
)
async def get_levels_number(callback_query: types.CallbackQuery,
                            state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    choice = callback_query.data
    async with state.proxy() as cake:
        cake['levels_number'] = choice

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=f'Количество уровней: {choice}',
                                reply_markup=None)

    markup = get_markup(SHAPES)
    await bot.send_message(callback_query.from_user.id,
                           'Выберите одну из форм торта',
                           disable_notification=True,
                           reply_markup=markup)
    await CreateCake.next()


@dp.callback_query_handler(
    lambda choice: choice.data in [shape.split()[0] for shape in SHAPES],
    state=CreateCake.shape
)
async def get_shape(callback_query: types.CallbackQuery,
                    state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    choice = callback_query.data
    async with state.proxy() as cake:
        cake['shape'] = choice
    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=f'Форма торта: {choice}')
    markup = get_markup(TOPPINGS)
    await bot.send_message(callback_query.from_user.id,
                           'Выберите один из представленных видов топинга',
                           disable_notification=True,
                           reply_markup=markup)
    await CreateCake.next()


@dp.callback_query_handler(
    lambda choice: choice.data in [topping.split()[0] for topping in TOPPINGS],
    state=CreateCake.topping
)
async def get_topping(callback_query: types.CallbackQuery,
                      state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    choice = callback_query.data
    async with state.proxy() as cake:
        cake['topping'] = choice
    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=f'Топпинг: {choice.replace("_", " ")}')
    markup = get_markup(BERRIES)
    continue_button = types.InlineKeyboardButton('Без ягод',
                                                 callback_data='Без ягод')
    markup.add(continue_button)

    await bot.send_message(callback_query.from_user.id,
                           'Добавьте ягоды по желанию',
                           disable_notification=True,
                           reply_markup=markup)
    await CreateCake.next()


@dp.callback_query_handler(
    lambda choice: choice.data == 'Без ягод',
    state=CreateCake.berries
)
async def get_berries(callback_query: types.CallbackQuery,
                      state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as cake:
        cake['berries'] = None

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text='Без ягод')

    await send_message_with_decors(callback_query.from_user.id)
    await CreateCake.next()


@dp.callback_query_handler(
    lambda choice: choice.data in [berry.split()[0] for berry in BERRIES],
    state=CreateCake.berries
)
async def get_berries(callback_query: types.CallbackQuery,
                      state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    choice = callback_query.data
    async with state.proxy() as cake:
        try:
            cake['berries'].append(choice)
        except KeyError:
            cake['berries'] = [choice]
        selected_berries = cake['berries']
    all_berries_selected = False
    if len(selected_berries) < len(BERRIES):
        not_selected_berries = [berry for berry in BERRIES if
                                berry.split()[0] not in selected_berries]
        markup = get_markup(not_selected_berries)
        continue_button = types.InlineKeyboardButton(
            'Продолжить',
            callback_data='Продолжить'
        )
        markup.add(continue_button)
        text = 'Можно добавить еще ягод или продолжить собирать торт'
    else:
        all_berries_selected = True
        markup = None
        text = f"Добавленные ягоды: {', '.join(selected_berries)}"

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=markup)
    if all_berries_selected:
        await send_message_with_decors(callback_query.from_user.id)
        await CreateCake.next()


@dp.callback_query_handler(
    lambda choice: choice.data == 'Продолжить',
    state=CreateCake.berries
)
async def get_berries(callback_query: types.CallbackQuery,
                      state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as cake:
        selected_berries = cake['berries']

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text="Добавленные ягоды: "
                                     f"{', '.join(selected_berries)}")
    await send_message_with_decors(callback_query.from_user.id)
    await CreateCake.next()


@dp.callback_query_handler(
    lambda choice: choice.data == 'Без декора',
    state=CreateCake.decor
)
async def get_decor(callback_query: types.CallbackQuery,
                    state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as cake:
        cake['decor'] = None

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text='Без декора')

    await send_message_with_title(callback_query.from_user.id, state)
    await CreateCake.next()


@dp.callback_query_handler(
    lambda choice: choice.data in [decor.split()[0] for decor in DECORS],
    state=CreateCake.decor
)
async def get_decor(callback_query: types.CallbackQuery,
                    state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    choice = callback_query.data
    async with state.proxy() as cake:
        try:
            cake['decor'].append(choice)
        except KeyError:
            cake['decor'] = [choice]
        selected_decors = cake['decor']
    all_decors_selected = False
    if len(selected_decors) < len(DECORS):
        not_selected_decors = [decor for decor in DECORS if
                               decor.split()[0] not in selected_decors]
        markup = get_markup(not_selected_decors)
        continue_button = types.InlineKeyboardButton(
            'Продолжить',
            callback_data='Продолжить'
        )
        markup.add(continue_button)
        text = 'Можно добавить еще элементов декора или ' \
               'продолжить собирать торт'
    else:
        all_decors_selected = True
        markup = None
        text = f"Добавленный декор: {', '.join(selected_decors)}"

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=markup)
    if all_decors_selected:
        await send_message_with_title(callback_query.from_user.id, state)
        await CreateCake.next()


@dp.callback_query_handler(
    lambda choice: choice.data == 'Продолжить',
    state=CreateCake.decor
)
async def get_decor(callback_query: types.CallbackQuery,
                    state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as cake:
        selected_decors = cake['decor']

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text='Добавленный декор: '
                                     f'{", ".join(selected_decors)}')

    await send_message_with_title(callback_query.from_user.id, state)
    await CreateCake.next()


@dp.callback_query_handler(
    lambda choice: choice.data == 'Без надписи',
    state=CreateCake.title
)
async def get_title(callback_query: types.CallbackQuery,
                    state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as cake:
        cake['title'] = 'Без надписи'

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text='Без надписи')
    await finish_cake_collecting(callback_query.from_user.id, state)


@dp.message_handler(
    content_types=types.ContentTypes.TEXT,
    state=CreateCake.title
)
async def get_title(message: types.Message, state: FSMContext):
    title = message.text
    async with state.proxy() as cake:
        cake['title'] = title
        message_id = cake['title_message_id']
    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=message_id,
                                text=f'Надпись на торте: {title}')
    await finish_cake_collecting(message.from_user.id, state)


async def finish_cake_collecting(chat_id, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                         resize_keyboard=True,
                                         row_width=2)
    order_button = types.InlineKeyboardButton('Заказать торт')
    reassemble_button = types.InlineKeyboardButton('Собрать торт заново')
    keyboard.add(order_button, reassemble_button)
    price = 1000
    await bot.send_message(chat_id,
                           f'Итоговая цена заказа: {price} р.',
                           disable_notification=True,
                           reply_markup=keyboard)
    await state.finish()
