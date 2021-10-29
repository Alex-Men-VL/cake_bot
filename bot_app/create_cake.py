from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from .app import dp, bot
from .helpers import LEVELS, SHAPES, TOPPINGS, BERRIES, DECORS
from .helpers import get_markup, send_message_with_decors, \
    send_message_with_title, send_message_with_comment, \
    send_message_with_address, send_message_with_date, finish_cake_collecting


class CreateCake(StatesGroup):
    levels_number = State()
    shape = State()
    topping = State()
    berries = State()
    decor = State()
    title = State()
    comment = State()
    address = State()
    date = State()
    time = State()


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
    await send_message_with_comment(callback_query.from_user.id, state)
    await CreateCake.next()


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
    await send_message_with_comment(message.from_user.id, state)
    await CreateCake.next()


@dp.callback_query_handler(
    lambda choice: choice.data == 'Без комментария',
    state=CreateCake.comment
)
async def get_comment(callback_query: types.CallbackQuery,
                      state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as cake:
        cake['comment'] = 'Без комментария'

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text='Без комментария')
    await send_message_with_address(callback_query.from_user.id, state)
    await CreateCake.next()


@dp.message_handler(
    content_types=types.ContentTypes.TEXT,
    state=CreateCake.comment
)
async def get_comment(message: types.Message, state: FSMContext):
    comment = message.text
    async with state.proxy() as cake:
        cake['comment'] = comment
        message_id = cake['comment_message_id']

    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=message_id,
                                text=f'Комментарий к заказу: {comment}')
    await send_message_with_address(message.from_user.id, state)
    await CreateCake.next()


@dp.callback_query_handler(
    lambda choice: choice.data == 'Доставить по этому адресу',
    state=CreateCake.address
)
async def get_address(callback_query: types.CallbackQuery,
                      state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as cake:
        address = cake['address']

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=f'Доставить по адресу: {address}')

    await send_message_with_date(callback_query.from_user.id, state)
    await CreateCake.next()


@dp.message_handler(
    content_types=types.ContentTypes.TEXT,
    state=CreateCake.address
)
async def get_address(message: types.Message, state: FSMContext):
    address = message.text
    async with state.proxy() as cake:
        cake['address'] = address
        message_id = cake['address_message_id']

    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=message_id,
                                text=f'Доставить по адресу: {address}')

    await send_message_with_date(message.from_user.id, state)
    await CreateCake.next()


@dp.message_handler(
    content_types=types.ContentTypes.TEXT,
    state=CreateCake.date
)
async def get_date(message: types.Message, state: FSMContext):
    date = message.text
    async with state.proxy() as cake:
        cake['date'] = date
        message_id = cake['date_message_id']

    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=message_id,
                                text=f'Дата доставки: {date}')

    message = await bot.send_message(
        message.from_user.id,
        'Введите время доставки',
        disable_notification=True,
        reply_markup=None
    )
    async with state.proxy() as cake:
        cake['time_message_id'] = message.message_id
    await CreateCake.next()


@dp.message_handler(
    content_types=types.ContentTypes.TEXT,
    state=CreateCake.time
)
async def get_time(message: types.Message, state: FSMContext):
    time = message.text
    async with state.proxy() as cake:
        cake['time'] = time
        message_id = cake['time_message_id']

    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=message_id,
                                text=f'Время доставки: {time}')
    await finish_cake_collecting(message.from_user.id, state)
