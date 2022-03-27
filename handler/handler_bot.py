from aiogram import types, Dispatcher

from help.help_file import dp, bot

async def command_start(message: types.Message):
    print('user start')
    await message.answer('Здравствуйте! Я Ваш мобильный ассистент!')

def register_handlers(dp: Dispatcher):
    try:
        dp.register_message_handler(command_start, commands='start')
    except Exception:
        print('ERROR')
