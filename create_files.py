import os

with open("database/db.py", "w", encoding="utf-8") as f:
    f.write("""import aiosqlite
from config import DB_PATH
import os

async def init_db():
    os.makedirs("database", exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                balance INTEGER DEFAULT 0,
                session_string TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                category TEXT,
                quantity INTEGER,
                price INTEGER,
                status TEXT DEFAULT 'pending', -- pending, processing, completed
                registered_count INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS registered_usernames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                username TEXT
            )
        ''')
        await db.commit()
""")

with open("bot/main.py", "w", encoding="utf-8") as f:
    f.write("""import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from bot.handlers import router as main_router
from bot.payments import router as payments_router
from database.db import init_db

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(main_router)
    dp.include_router(payments_router)
    
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
""")

with open("bot/handlers.py", "w", encoding="utf-8") as f:
    f.write("""from aiogram import Router, F
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
""")

with open("worker/generator.py", "w", encoding="utf-8") as f:
    f.write("""import itertools

def generate_usernames(base_word, limit=100):
    suffixes = ["chi", "lar", "lash", "im", "iy", "uz", "go", "uzb", "pro", "bot"]
    prefixes = ["uz", "the", "my", "pro", "best"]
    
    results = set()
    results.add(base_word)
    
    # Suffixes
    for suf in suffixes:
        results.add(f"{base_word}{suf}")
        
    # Prefixes
    for pref in prefixes:
        results.add(f"{pref}{base_word}")
        
    # Double
    for suf in suffixes:
        for pref in prefixes:
            results.add(f"{pref}{base_word}{suf}")
            
    return list(results)[:limit]
""")

print("Phase 1 files created")
