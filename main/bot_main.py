from aiogram.utils import executor

from help.help_file import dp
from client.client_part import *

async def on_startup(_):
    print('Bot connected')

register_handlers_client(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)