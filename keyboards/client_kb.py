from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from datetime import date

from orm_method.orm_fucntion import search_client_with_alphabet, search_history_visit_client


def check_client_in_db():
    inline = InlineKeyboardMarkup(row_width=2)
    [inline.insert(InlineKeyboardButton(text=str(element), callback_data=callback_data))
     for element, callback_data in zip(['Да', 'Нет'], ['yes', 'not'])]
    return inline

def chooce_year(reanswear: str=None):
    inline = InlineKeyboardMarkup(row_width=2)
    if reanswear != 'another':
        element = InlineKeyboardButton(text='Поточный', callback_data=str(date.today().year))
        inline.insert(element)
        element = InlineKeyboardButton(text='Другой', callback_data='another')
        inline.insert(element)
    elif reanswear == 'another':
        [inline.insert(
            InlineKeyboardButton(text=str(year), callback_data=str(year))
        ) for year in range(2018, int(date.today().year)+4)]
    return inline

def choose_month():
    inline = InlineKeyboardMarkup(row_width=2)
    for element in ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
     'Июль', 'Август', 'Сеньтябрь', 'Октябрь', 'Ноябрь', 'Январь']:
        element = InlineKeyboardButton(text=element, callback_data=element)
        inline.insert(element)
    return inline

def choose_day_in_month(month: str):
    inline = InlineKeyboardMarkup(row_width=3)
    day_in_month = {'Январь': 31, 'Февраль': 28, 'Март': 31, 'Апрель': 30, 'Май': 31, 'Июнь': 30,
     'Июль': 31, 'Август': 31, 'Сентябрь': 30, 'Октябрь': 31, 'Ноябрь': 30, 'Декабрь': 31}
    for element in range(1, day_in_month.get(month)+1):
        element = InlineKeyboardButton(text=str(element), callback_data=str(element))
        inline.insert(element)
    return inline

def choose_time():
    inline = InlineKeyboardMarkup(row_width=2)
    for element in range(9, 22):
        keyboard = InlineKeyboardButton(text=f'{element}:00', callback_data=f'{element}:00')
        inline.insert(keyboard)
        keyboard = InlineKeyboardButton(text=f'{element}:30', callback_data=f'{element}:30')
        inline.insert(keyboard)
    return inline

def choose_new_client_or_not():
    inline = InlineKeyboardMarkup(row_width=2)
    element = InlineKeyboardButton(text='Клиент уже есть в базе', callback_data='yes')
    inline.insert(element)
    element = InlineKeyboardButton(text='Клиент еще не был записан', callback_data='not')
    inline.insert(element)
    return inline

def choose_alphabet_for_search():
    temp_str = 'абвгдеёжзийклмнопрстуфхцчшщэюя'.upper()
    inline = InlineKeyboardMarkup(row_width=4)
    [inline.insert(InlineKeyboardButton(text=element, callback_data=element)) for element in temp_str]
    return inline

def choose_client_in_db(letter):
    inline = InlineKeyboardMarkup(row_width=2)
    for element in search_client_with_alphabet(letter):
        inline.insert(InlineKeyboardButton(text=f'{element.last_name} {element.first_name}',
                                           callback_data=f'{element.last_name} {element.first_name}'))
    return inline

def inline_cancel():
    inline = InlineKeyboardMarkup(row_width=1)
    inline.insert(InlineKeyboardButton(text='Фото не требуется', callback_data='None'))
    return inline

def inline_date_visit(client_id):
    inline = InlineKeyboardButton(row_width=2)
    for element in search_history_visit_client(client_id):
        inline.insert(InlineKeyboardButton(text=element.date, callback_data=element.date))
    return inline