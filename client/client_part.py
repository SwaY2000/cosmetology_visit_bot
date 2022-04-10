from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.types import ContentType
from aiogram.types.callback_query import CallbackQuery

from help.help_file import dp, bot
from keyboards.client_kb import check_client_in_db, chooce_year, choose_month, choose_day_in_month, \
    choose_new_client_or_not, choose_time, choose_alphabet_for_search, choose_client_in_db, inline_cancel
from orm_method.orm_fucntion import *

class FSMVisit(StatesGroup):
    yes_or_not = State()
    choose_letter = State()
    client = State()
    year = State()
    month = State()
    day = State()
    time = State()
    cosmetics_procedure = State()
    photo_sticker_path = State()
    photo_after_path = State()

class FSMHistory(StatesGroup):
    letter = State()
    client = State()

async def start_add_visit(message: types.Message):
    """Kb inline, entry client in db?"""
    await FSMVisit.next()
    await message.reply('У клиента уже есть анкета?', reply_markup=check_client_in_db())

async def callback_check_if_client_entry_db(callback_query: types.CallbackQuery, state: FSMContext):
    """Handler have client in db or not"""
    async with state.proxy() as data:
        if callback_query.data == 'yes':
            data['yes_or_not'] = callback_query.data
            await callback_query.message.edit_text('Выберите букву, на которую начинается фамилия клиента',
                                                   reply_markup=choose_alphabet_for_search())
            await FSMVisit.next()

        elif callback_query.data == 'not':
            data['yes_or_not'] = callback_query.data
            await callback_query.message.edit_text('обработка')
            await FSMVisit.next()

async def callback_search_client_alphabet(callback_query: types.CallbackQuery, state: FSMContext):
    """This is handler search client with help alphabet"""
    async with state.proxy() as data:
        data['choose_letter'] = 'yes'
    await callback_query.message.edit_text('Выберите клиента', reply_markup=choose_client_in_db(callback_query.data))
    await FSMVisit.next()

async def temp_funct_for_choose_letter(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['choose_letter'] = 'yes'
    await message.reply('Введите имя, фамилию, номер телефона клиента')
    await FSMVisit.next()

async def add_client_in_db(message: types.Message, state: FSMContext):
    """handler two way: create client or search client in db"""
    print(999888)
    client_dict = {}
    client_info = message.text

    index = client_info.index(' ')
    client_dict['first_name'] = client_info[0:index]
    client_info = client_info[index:].replace(' ', '', 1)
    index = client_info.index(' ')
    client_dict['last_name'], client_dict['phone_number'] = client_info[0:index], client_info[index:].replace(' ', '', 1)

    async with state.proxy() as data:
        await message.reply('Anames') #BUG
        client_dict['anames'] = message.text
        create_new_client(client_dict['first_name'], client_dict['last_name'],
                          client_dict['phone_number'], client_dict['anames'])
        data['client'] = search_client(client_dict['first_name'], client_dict['last_name']).client_id
        print(search_client(client_dict['first_name'], client_dict['last_name']).client_id, 999)
        await FSMVisit.next()

        await message.reply('Выберите год', reply_markup=chooce_year())

async def callback_return_client_from_db(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['client'] = search_client(callback_query.data[callback_query.data.index(' ')+1:], callback_query.data[:callback_query.data.index(' ')]).client_id
        await FSMVisit.next()
        await callback_query.message.edit_text('Выберите год', reply_markup=chooce_year())

async def callback_choose_year(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data == 'another':
            inline_choose_year = chooce_year('another')
            await callback_query.message.edit_text('Выберите год',
                                                   reply_markup=inline_choose_year)
            return
        data['year'] = callback_query.data
    await FSMVisit.next()
    await callback_query.message.edit_text('За какой месяц хотите сделать запись?', reply_markup=choose_month())

async def callback_choose_month(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['month'] = callback_query.data
    await callback_query.message.edit_text('Выберите день', reply_markup=choose_day_in_month(str(callback_query.data)))
    await FSMVisit.next()

async def callback_choose_day(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['day'] = callback_query.data
    await callback_query.message.edit_text('Выберите время', reply_markup=choose_time())
    await FSMVisit.next()

async def callback_choose_time(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = callback_query.data
    await callback_query.message.reply('Опишите процедуру')
    await FSMVisit.next()

async def message_parse_procedure(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['cosmetics_procedure'] = message.text
    await message.reply('Отправьте фото стикера', reply_markup=inline_cancel())
    await FSMVisit.next()

async def download_photo_cosmetics_sticker(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.photo[-1].download(destination_file=f"templates/sticker/{search_last_visit_id()+1}.jpg")
        data['photo_sticker'] = f'{search_last_visit_id()+1}.jpg'
        await message.reply('Отправьте фото пациент после процедуры', reply_markup=inline_cancel())
    await FSMVisit.next()

async def callback_cancel_sticker(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['photo_sticker'] = callback_query.data
    await callback_query.message.reply('Отправьте фото пациент после процедуры', reply_markup=inline_cancel())
    await FSMVisit.next()

async def download_photo_after_procedure(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.photo[-1].download(destination_file=f"templates/after_procedure/{search_last_visit_id()+1}.jpg")
        data['photo_after'] = f'{search_last_visit_id()+1}.jpg'
    await message.reply('Готово')
    await state.finish()

async def callback_cancel_after_procedure(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['photo_sticker'] = callback_query.data
    await callback_query.message.reply('Готово')
    await state.finish()


def start_view_history_visit(message: types.Message):
    await FSMHistory.next()
    await message.reply('Выберите букву, на которую начинается фамилия клиента',
                        reply_markup=choose_alphabet_for_search())

async def callback_choose_letter_for_search(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['letter'] = callback_query.data
    await callback_query.message.reply('Выберите букву, на которую начинается фамилия клиента',
                                       reply_markup=choose_client_in_db(callback_query.data))

async def callback_choose_client(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['client'] = search_client(callback_query.data[callback_query.data.index(' ')+1:],
                                       callback_query.data[:callback_query.data.index(' ')]).client_id
    await callback_query.message.reply('Выберите букву, на которую начинается фамилия клиента',
                                       reply_markup=choose_client_in_db(callback_query.data))

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_add_visit, commands=['add'], state=None)
    dp.register_callback_query_handler(callback_check_if_client_entry_db, state=FSMVisit.yes_or_not)
    dp.register_callback_query_handler(callback_search_client_alphabet, state=FSMVisit.choose_letter)
    dp.register_message_handler(temp_funct_for_choose_letter, state=FSMVisit.choose_letter)
    dp.register_message_handler(add_client_in_db, state=FSMVisit.client)
    dp.register_callback_query_handler(callback_return_client_from_db, state=FSMVisit.client)
    dp.register_callback_query_handler(callback_choose_year, state=FSMVisit.year)
    dp.register_callback_query_handler(callback_choose_month, state=FSMVisit.month)
    dp.register_callback_query_handler(callback_choose_day, state=FSMVisit.day)
    dp.register_callback_query_handler(callback_choose_time, state=FSMVisit.time)
    dp.register_message_handler(message_parse_procedure, state=FSMVisit.cosmetics_procedure)
    dp.register_message_handler(download_photo_cosmetics_sticker, state=FSMVisit.photo_sticker_path, content_types=ContentType.PHOTO)
    dp.register_callback_query_handler(callback_cancel_sticker, state=FSMVisit.photo_sticker_path)
    dp.register_message_handler(download_photo_after_procedure, state=FSMVisit.photo_after_path, content_types=ContentType.PHOTO)
    dp.register_callback_query_handler(callback_cancel_after_procedure, state=FSMVisit.photo_after_path)

    ####################################################################################################################
    dp.register_message_handler(start_add_visit, commands=['history'], state=None)
    dp.register_callback_query_handler(callback_choose_letter_for_search, state=FSMHistory.letter)
    dp.register_callback_query_handler(callback_choose_client, state=FSMHistory.client)

