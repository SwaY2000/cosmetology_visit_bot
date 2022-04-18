from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.dispatcher.webhook import DeleteMessage
from aiogram.types import ContentType
from aiogram.types.callback_query import CallbackQuery

from help.help_file import dp, bot
from keyboards.client_kb import check_client_in_db, chooce_year, choose_month, choose_day_in_month, \
    choose_new_client_or_not, choose_time, choose_alphabet_for_search, choose_client_in_db, inline_cancel, \
    inline_date_visit, inline_more_date, inline_cancel_done, cancel_fsm
from orm_method.orm_fucntion import *

INTRODUCE_MESSAGE = f"""Здравствуйте, я помогу Вам с записью посещений Ваших клиентов.
Для записи посещения клиента, выберите \"/add\"
Для просмотра историю посещений, выберите \"/history\""""

async def for_end_state(message_delete, state):
    try:
        await bot.delete_message(chat_id=message_delete.chat.id,
                                 message_id=message_delete.message_id)
        await bot.delete_message(chat_id=message_delete.chat.id,
                                 message_id=message_delete.message_id-1)
    except Exception:
        pass
    await state.finish()
    await message_delete.answer(INTRODUCE_MESSAGE)
    return

global client_dict
client_dict = {}

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
    history = State()

async def start_bot(message: types.Message):
    await message.delete()
    await message.answer(INTRODUCE_MESSAGE)

async def start_add_visit(message: types.Message):
    """Kb inline, entry client in db?"""
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await FSMVisit.next()
    await message.reply('У клиента уже есть анкета?', reply_markup=check_client_in_db())
    await message.delete()

async def callback_check_if_client_entry_db(callback_query: types.CallbackQuery, state: FSMContext):
    """Handler have client in db or not"""
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    async with state.proxy() as data:
        if callback_query.data == 'yes':
            data['yes_or_not'] = callback_query.data
            await callback_query.message.edit_text('Выберите букву, на которую начинается фамилия клиента',
                                                   reply_markup=choose_alphabet_for_search())
            await FSMVisit.next()

        elif callback_query.data == 'not':
            data['yes_or_not'] = callback_query.data
            await FSMVisit.next()
            await temp_funct_for_choose_letter(callback_query.message, state)

async def callback_search_client_alphabet(callback_query: types.CallbackQuery, state: FSMContext):
    """This is handler search client with help alphabet"""
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    global page
    page = 0
    async with state.proxy() as data:
        data['choose_letter'] = 'yes'
        await callback_query.message.edit_text('Выберите клиента', reply_markup=choose_client_in_db(callback_query.data, 0))
        await FSMVisit.next()

async def temp_funct_for_choose_letter(message: types.Message, state: FSMContext):
    await message.delete()
    async with state.proxy() as data:
        data['choose_letter'] = 'not'
    await message.answer('Введите имя, фамилию, номер телефона клиента', reply_markup=cancel_fsm())
    await FSMVisit.next()

async def add_client_in_db(message: types.Message, state: FSMContext, client_dict=client_dict):
    """handler create client in db"""
    if client_dict.get('anames'):
        async with state.proxy() as data:
            client_dict['anames'] = message.text
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            await message.delete()
            create_new_client(client_dict['first_name'], client_dict['last_name'],
                              client_dict['phone_number'], client_dict['anames'])
            data['client'] = search_client(client_dict['first_name'], client_dict['last_name']).client_id
            await FSMVisit.next()
            await message.answer('Выберите год', reply_markup=chooce_year())

    elif client_dict.get('anames') == None:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        client_info = message.text
        index = client_info.index(' ')
        client_dict['first_name'] = client_info[0:index]
        client_info = client_info[index:].replace(' ', '', 1)
        index = client_info.index(' ')
        client_dict['last_name'], client_dict['phone_number'] = client_info[0:index], \
                                                                client_info[index:].replace(' ', '', 1)
        client_dict['anames'] = ' '
        await message.delete()
        await message.answer('Есть ли у клиента аллергия?', reply_markup=cancel_fsm())
        return

async def callback_return_client_from_db(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    async with state.proxy() as data:
        if callback_query.data in ['<', '>']:
            page += 1
            await callback_query.message.edit_text('Выберите клиента',
                                                   reply_markup=choose_client_in_db(callback_query.data, page))
            return
        data['client'] = search_client(callback_query.data[callback_query.data.index(' ') + 1:],
                                       callback_query.data[:callback_query.data.index(' ')]).client_id
        await callback_query.message.edit_text('Выберите год', reply_markup=chooce_year())
        await FSMVisit.next()

async def callback_choose_year(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
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
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    async with state.proxy() as data:
        data['month'] = callback_query.data
    await callback_query.message.edit_text('Выберите день', reply_markup=choose_day_in_month(str(callback_query.data)))
    await FSMVisit.next()

async def callback_choose_day(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    async with state.proxy() as data:
        data['day'] = callback_query.data
    await callback_query.message.edit_text('Выберите время', reply_markup=choose_time())
    await FSMVisit.next()

async def callback_choose_time(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    async with state.proxy() as data:
        data['time'] = callback_query.data
    await callback_query.message.edit_text('Опишите процедуру', reply_markup=cancel_fsm())
    await FSMVisit.next()

async def callback_cancel_fsm(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)

async def message_parse_procedure(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    async with state.proxy() as data:
        data['cosmetics_procedure'] = message.text
    await message.delete()
    await message.answer('Отправьте фото стикера', reply_markup=inline_cancel())
    await FSMVisit.next()

async def download_photo_cosmetics_sticker(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.photo[-1].download(destination_file=f"templates/sticker/{search_last_visit_id()+1}.jpg")
        data['photo_sticker_path'] = f'{search_last_visit_id()+1}.jpg'
        await message.edit_text('Отправьте фото пациент после процедуры', reply_markup=inline_cancel())
    await FSMVisit.next()

async def callback_cancel_sticker(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    async with state.proxy() as data:
        data['photo_sticker_path'] = callback_query.data
    await callback_query.message.edit_text('Отправьте фото пациента после процедуры', reply_markup=inline_cancel())
    await FSMVisit.next()

async def download_photo_after_procedure(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.photo[-1].download(destination_file=f"templates/after_procedure/{search_last_visit_id()+1}.jpg")
        data['photo_after_path'] = f'{search_last_visit_id()+1}.jpg'
        add_new_visit(data['client'], f'{data["year"]}-{data["month"]}-{data["day"]}',
                      data['time'], data['cosmetics_procedure'], data['photo_sticker_path'],
                      data['photo_after_path'])
    await message.edit_text('Готово')
    await state.finish()

async def callback_cancel_after_procedure(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    if callback_query.data == 'continue':
        try:
            [await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id-i) for i in range(0, 4)]
        except Exception:
            pass
        finally:
            await state.finish()
            await callback_query.message.answer(INTRODUCE_MESSAGE)
            return
    async with state.proxy() as data:

        data['photo_after_path'] = callback_query.data
        add_new_visit(data['client'], f'{data["year"]}-{data["month"]}-{data["day"]}',
                      data['time'], data['cosmetics_procedure'], data['photo_sticker_path'],
                      data['photo_after_path'])
    await callback_query.message.edit_text('Готово', reply_markup=inline_cancel_done())
    return

##########################################################

async def start_view_history_visit(message: types.Message):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await FSMHistory.next()
    await message.answer('Выберите букву, на которую начинается фамилия клиента',
                         reply_markup=choose_alphabet_for_search())

async def callback_choose_letter_for_search(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    async with state.proxy() as data:
        data['letter'] = callback_query.data
    await callback_query.message.edit_text('Выберите клиента',
                                           reply_markup=choose_client_in_db(callback_query.data, 0))
    global page
    page = 0
    await callback_more_client_for_history(callback_query, state, page=page)

async def callback_more_client_for_history(callback_query: types.CallbackQuery, state: FSMContext, page):
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    if callback_query.data in ['<', '>']:
        page += 1
        await callback_query.message.edit_text('Выберите клиента',
                                               reply_markup=choose_client_in_db(callback_query.data, page))
        return
    else:
        del page
        await FSMHistory.next()

async def callback_choose_client(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    async with state.proxy() as data:
        client_obj_orm = search_client(callback_query.data[callback_query.data.index(' ')+1:],
                                       callback_query.data[:callback_query.data.index(' ')])
        data['client'] = client_obj_orm
    await callback_query.message.edit_text('Выберите дату визита',
                                       reply_markup=inline_date_visit(client_obj_orm.client_id))
    await FSMHistory.next()

async def callback_history_visit(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        await for_end_state(callback_query.message, state)
        return
    async with state.proxy() as data:
        if callback_query.data == 'None':
            await callback_query.message.edit_text('Выберите дату визита',
                                               reply_markup=inline_date_visit(data['client'].client_id))  # add cancel
            return
        elif callback_query.data == 'Done':
            await state.finish()
            return
        data['history'] = callback_query.data
        temp_db = search_history_visit_client_filter_by_date([data['client'].first_name, data['client'].last_name],
                                                             callback_query.data)
        media = None
        if temp_db.path_to_photo_sticker != 'None':
            media = types.MediaGroup()
            media.attach_photo(types.InputFile(f'templates/sticker/{temp_db.path_to_photo_sticker}'), 'Фотография стикера')
            if temp_db.path_to_photo_after_procedure != None:
                media.attach_photo(types.InputFile(f'templates/after_procedure/{temp_db.path_to_photo_after_procedure}'), 'Фотография после процедуры')

        elif temp_db.path_to_photo_after_procedure != None:
            media = types.MediaGroup()
            media.attach_photo(types.InputFile(f'templates/after_procedure/{temp_db.path_to_photo_after_procedure}'), 'Фотография после процедуры')
        await callback_query.message.edit_text(f'Клиент: {data["client"].last_name}, {data["client"].first_name} \n'
                                           f'Процедура: {temp_db.procedure} \n'
                                           f'Время визита: {temp_db.time_visit}',
                                           reply_markup=inline_more_date())
        if media is not None:
            await bot.send_media_group(callback_query.message.chat.id, media=media)



def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_bot, commands=['start'])
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
    dp.register_callback_query_handler(callback_cancel_fsm, state=FSMVisit.cosmetics_procedure)
    dp.register_message_handler(message_parse_procedure, state=FSMVisit.cosmetics_procedure)
    dp.register_message_handler(download_photo_cosmetics_sticker, state=FSMVisit.photo_sticker_path, content_types=ContentType.PHOTO)
    dp.register_callback_query_handler(callback_cancel_sticker, state=FSMVisit.photo_sticker_path)
    dp.register_message_handler(download_photo_after_procedure, state=FSMVisit.photo_after_path, content_types=ContentType.PHOTO)
    dp.register_callback_query_handler(callback_cancel_after_procedure, state=FSMVisit.photo_after_path)
    ####################################################################################################################
    dp.register_message_handler(start_view_history_visit, commands=['history'], state=None)
    dp.register_callback_query_handler(callback_choose_letter_for_search, state=FSMHistory.letter)
    dp.register_callback_query_handler(callback_choose_client, state=FSMHistory.client)
    dp.register_callback_query_handler(callback_history_visit, state=FSMHistory.history)