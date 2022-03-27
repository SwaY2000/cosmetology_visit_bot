from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher

from keyboards.client_kb import check_client_in_db, chooce_year, choose_month, choose_day_in_month, \
    choose_new_client_or_not
from orm_method.orm_fucntion import *


class FSMAdmin(StatesGroup):
    client = State()#checking if client entry in db
    year = State()
    month = State()
    day = State()
    time = State()
    cosmetics_procedur = State()
    info_procedur = State()

async def start_add(message: types.Message):
    await FSMAdmin.next()
    await message.reply('У клиента уже есть анкета?', reply_markup=check_client_in_db())

async def check_client(message: types.Message, callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data == 'yes':
            await message.reply('Введите имя и фамилию клиента')
            await FSMAdmin.next()
        elif data == 'not':
            await message.reply('Введите имя, фамилию, номер телефона клиента')
            await FSMAdmin.next()
    await FSMAdmin.next()
    await callback_query.message.edit_text('Выберите за какой год будет запись?', reply_markup=chooce_year())

async def client_entry_db(message: types.Message, state: FSMContext):
    client_dict = {}
    client_info = message.text

    if client_info.count(' ') <= 1:
        index = client_info.index(' ')
        client_dict['first_name'], client_dict['last_name'] = client_info[0:index], client_info[index:]

    elif client_info.count(' ') > 1:
        index = client_info.index(' ')
        client_dict['first_name'] = client_info[0:index]
        client_info = client_info[index:].replace(' ', '', 1)
        index = client_info.index(' ')
        client_dict['last_name'], client_dict['phone_number'] = client_info[0:index], client_info[index:].replace(' ', '', 1)

    async with state.proxy() as data:
        if len(client_dict) <= 2:
            await message.reply('Anames')
            client_dict['anames'] = message.text
            create_new_client(client_dict['first_name'], client_dict['last_name'],
                              client_dict['phone_number'], client_dict['anames'])
            data['client'] = search_client(client_dict['first_name'], client_dict['last_name']).client_id
            await FSMAdmin.next()

        elif len(client_dict) > 2:
            data['client'] = search_client(client_dict['first_name'], client_dict['last_name']).client_id
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


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_change, commands=['entry'], state=None)
    dp.register_callback_query_handler(callback_change_day, state=FSMAdmin.day)
    dp.register_callback_query_handler(callback_change_essence, state=FSMAdmin.essence)
    dp.register_message_handler(change_sequence, state=FSMAdmin.sequence)
    dp.register_callback_query_handler(callback_yes_or_not, state=FSMAdmin.yes_or_no_comment)
    dp.register_message_handler(change_comment, state=FSMAdmin.comment)
    dp.register_callback_query_handler(callback_add_change, state=FSMAdmin.add_change)


