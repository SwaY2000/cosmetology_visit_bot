from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.types import ContentType
from aiogram.types.callback_query import CallbackQuery

from help.help_file import dp, bot

from keyboards.client_kb import check_client_in_db, chooce_year, choose_month, choose_day_in_month, \
    choose_new_client_or_not
from orm_method.orm_fucntion import *


class FSMAdmin(StatesGroup):
    yes_or_not = State()
    client = State()
    year = State()
    month = State()
    day = State()
    time = State()
    cosmetics_procedur = State()
    photo_sticker = State()
    photo_after = State()

async def start_add(message: types.Message):
    await FSMAdmin.next()
    await message.reply('У клиента уже есть анкета?', reply_markup=check_client_in_db())

async def check_client(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback_query.data == 'yes':
            data['yes_or_not'] = callback_query.data
            await callback_query.message.edit_text('Введите имя и фамилию клиента')
            await FSMAdmin.next()
        elif callback_query.data == 'not':
            data['yes_or_not'] = callback_query.data
            await callback_query.message.edit_text('Введите имя, фамилию, номер телефона клиента')
            await FSMAdmin.next()

async def client_entry_db(message: types.Message, state: FSMContext):
    client_dict = {}
    client_info = message.text

    if client_info.count(' ') <= 1:
        index = client_info.index(' ')
        client_dict['first_name'], client_dict['last_name'] = client_info[0:index], client_info[index+1:]

    elif client_info.count(' ') > 1:
        index = client_info.index(' ')
        client_dict['first_name'] = client_info[0:index]
        client_info = client_info[index:].replace(' ', '', 1)
        index = client_info.index(' ')
        client_dict['last_name'], client_dict['phone_number'] = client_info[0:index], client_info[index:].replace(' ', '', 1)

    async with state.proxy() as data:
        if len(client_dict) > 2:
            await message.reply('Anames')
            client_dict['anames'] = message.text
            create_new_client(client_dict['first_name'], client_dict['last_name'],
                              client_dict['phone_number'], client_dict['anames'])
            data['client'] = search_client(client_dict['first_name'], client_dict['last_name']).client_id
            print(search_client(client_dict['first_name'], client_dict['last_name']).client_id)
            await FSMAdmin.next()

        elif len(client_dict) <= 2:
            data['client'] = search_client(client_dict['first_name'], client_dict['last_name']).client_id
            print(data['client'])
            await FSMAdmin.next()

        await message.reply('Выерите год', reply_markup=chooce_year())

async def callback_choose_year(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data == 'another':
            inline_choose_year = chooce_year('another')
            await callback_query.message.edit_text('Выберите год',
                                                   reply_markup=inline_choose_year)
            return
        data['year'] = callback_query.data
    await FSMAdmin.next()
    await callback_query.message.edit_text('За какой месяц хотите сделать запись?', reply_markup=choose_month())

async def callback_choose_month(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['month'] = callback_query.data
        await callback_query.message.edit_text('Выберите день', reply_markup=choose_day_in_month(str(callback_query.data)))
    await FSMAdmin.next()

async def callback_choose_day(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['day'] = callback_query.data
    await callback_query.message.edit_text('Выберите время', reply_markup=choose_new_client_or_not())
    await FSMAdmin.next()

async def add_entry_client(message: types.Message, callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = callback_query.data
        await message.reply('Опишите процедуру')
        await FSMAdmin.next()

async def cosmetics_procedur_choose(message: types.Message, callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['cosmetics_procedur'] = message.text
    await message.reply('Отправьте фото стикера')
    await FSMAdmin.next()

async def cosmetics_sticker(message: types.Message, callback_query: types.CallbackQuery, state: FSMContext):
    await message.photo[-1].download(destination="/tmp/somedir/")
    async with state.proxy() as data:
        data['cosmetics_procedur'] = message.text
    await message.reply('Отправьте фото стикера')
    await FSMAdmin.next()

async def cosmetics_after(message: types.Message, callback_query: types.CallbackQuery, state: FSMContext):
    await message.photo[-1].download(destination="/tmp/somedir/")
    async with state.proxy() as data:
        data['cosmetics_procedur'] = message.text
    await message.reply('Отправьте фото стикера')
    await state.finish()


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_add, commands=['add'], state=None)
    dp.register_callback_query_handler(check_client, state=FSMAdmin.yes_or_not)
    dp.register_message_handler(client_entry_db, state=FSMAdmin.client)
    dp.register_callback_query_handler(callback_choose_year, state=FSMAdmin.year)
    dp.register_callback_query_handler(callback_choose_month, state=FSMAdmin.month)
    dp.register_callback_query_handler(callback_choose_day, state=FSMAdmin.day)
    dp.register_message_handler(add_entry_client, state=FSMAdmin.time)
    dp.register_message_handler(cosmetics_procedur_choose, state=FSMAdmin.cosmetics_procedur)
    dp.register_message_handler(cosmetics_sticker, state=FSMAdmin.photo_sticker, content_types=ContentType.PHOTO) #content_types=ContentType.PHOTO
    dp.register_message_handler(cosmetics_after, state=FSMAdmin.photo_after, content_types=ContentType.PHOTO)

