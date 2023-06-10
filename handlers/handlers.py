from aiogram import Router
from aiogram.filters import Command, CommandStart, and_f, or_f
from aiogram.types import Message
from lexicon import LEXICON
from aiogram import F, Bot
from config import load_config
from handlers.gan import styling
import os
import tempfile
from aiogram.types import FSInputFile

# Инициализируем роутер уровня модуля
router: Router = Router()
USER_PHOTOS: dict[int, list[str]] = {}
url = "https://api.telegram.org/file/bot" + load_config().tg_bot.token + "/"


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    user_id = message.from_user.id
    await message.answer(text=LEXICON['/start'])
    if not USER_PHOTOS.get(user_id):
        USER_PHOTOS[user_id] = []


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON['/help'])


# Этот хэндлер срабатывает на команду /contacts
@router.message(Command(commands='contacts'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON['/contacts'])


# Этот хэндлер будет срабатывать на отправку боту фото в виде документа или просто фото
@router.message(or_f(and_f(F.document, lambda msg: msg.document.mime_type.startswith('image/')), F.photo))
async def process_doc(message: Message, bot: Bot):
    user_id = message.from_user.id
    if not USER_PHOTOS.get(user_id):
        USER_PHOTOS[user_id] = []

    USER_PHOTOS[user_id].append((await bot.get_file(message.photo[-1].file_id)).file_path)
    if len(USER_PHOTOS[user_id]) == 1:
        await message.answer(text=LEXICON['send_style'])
    else:
        await message.answer(text=LEXICON['loading'])
        stylized_image = await styling(content_path=url + USER_PHOTOS[user_id][0],
                                       style_path=url + USER_PHOTOS[user_id][1])

        # Сохранение изображения во временный файл
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False, dir='') as f:
            stylized_image.save(f.name)
            temp_filename = f.name

        temp_filename = temp_filename.split('\\')[-1]
        photo = FSInputFile(temp_filename)
        await message.answer(text=LEXICON['success'])
        # Отправка изображения с помощью message.answer_photo
        await bot.send_photo(chat_id=user_id, photo=photo)

        # Удаление временного файла
        os.remove(temp_filename)

        USER_PHOTOS[user_id] = []


# Этот хэндлер будет срабатывать на отправку остальных типов сообщений
@router.message()
async def process_other(message: Message):
    await message.answer(text=LEXICON['unsupported file'])
