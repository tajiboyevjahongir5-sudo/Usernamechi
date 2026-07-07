from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import aiosqlite
from config import DB_PATH, USERNAME_PRICE

router = Router()

@router.message(CommandStart())
async def start_cmd(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (message.from_user.id,))
        await db.commit()
    await message.answer("Xush kelibsiz! Bu bot orqali avtomatik qisqa va ma'noli usernamelarni sotib olishingiz mumkin.")
