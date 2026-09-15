from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite
import aiohttp
import random
import re
import string
from config import DB_PATH, USERNAME_PRICE, CODECRAFT_API_KEY, CODECRAFT_MODEL

router = Router()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Qisqa noyob so'z username")],
        [KeyboardButton(text="Turli ko'rinishdagi username")],
        [KeyboardButton(text="Ma'noli va chiroyli username")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Tanlang..."
)


class UsernameStates(StatesGroup):
    waiting_for_description = State()


from bot.words import generate_smart_username


def generate_short_username():
    length = random.randint(3, 5)
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


async def generate_codecraft_usernames(description: str, count: int = 10):
    if not CODECRAFT_API_KEY:
        raise RuntimeError("CODECRAFT_API_KEY sozlanmagan")

    prompt = f"""
Sen professional Telegram username generatorisan.
Foydalanuvchi uchun ma'noli, chiroyli, esda qoladigan va Telegramga mos username variantlarini yarat.

Foydalanuvchi xohishi: {description}

Faqat {count} ta variant qaytar.
Har bir variantni alohida qatorda yoz.
Username faqat lotin harflari, raqam va underscore (_) dan iborat bo'lsin.
5-32 ta belgidan oshmasin.
@ belgisi, izoh, emoji va bo'sh joy ishlatma.
"""

    payload = {
        "model": CODECRAFT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "max_tokens": 300,
    }

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            "https://codecraftapi.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {CODECRAFT_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        ) as response:
            try:
                data = await response.json()
            except Exception:
                data = {}

            if response.status >= 400:
                error = data.get("error", "CodeCraft API xatosi")
                if isinstance(error, dict):
                    error = error.get("message", "CodeCraft API xatosi")
                raise RuntimeError(str(error))

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("CodeCraft javob qaytarmadi")

    text = choices[0].get("message", {}).get("content", "")
    names = []

    for line in text.splitlines():
        matches = re.findall(
            r"(?<![A-Za-z0-9_])@?([A-Za-z][A-Za-z0-9_]{4,31})(?![A-Za-z0-9_])",
            line,
        )
        if matches:
            name = matches[0].lower()
            if name not in names:
                names.append(name)

    if not names:
        raise RuntimeError("Username variantlari topilmadi")

    return names[:count]


@router.message(CommandStart())
async def start_cmd(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, balance) VALUES (?, ?)",
            (message.from_user.id, USERNAME_PRICE),
        )
        await db.commit()

    await message.answer(
        "Xush kelibsiz! Bu bot orqali avtomatik qisqa va ma'noli usernamelarni "
        "sotib olishingiz mumkin.\n\nUsername turini tanlang:",
        reply_markup=keyboard,
    )


@router.message(F.text == "Qisqa noyob so'z username")
async def short_username_handler(message: Message):
    usernames = [f"@{generate_short_username()}" for _ in range(5)]
    response = "Mana sizga qisqa noyob usernamelar:\n\n" + "\n".join(usernames)
    await message.answer(response)


@router.message(F.text == "Turli ko'rinishdagi username")
async def various_username_handler(message: Message):
    usernames = [f"@{generate_smart_username()}" for _ in range(5)]
    response = "Mana sizga turli ko'rinishdagi usernamelar:\n\n" + "\n".join(usernames)
    await message.answer(response)


@router.message(F.text == "Ma'noli va chiroyli username")
async def meaningful_username_start(message: Message, state: FSMContext):
    await state.set_state(UsernameStates.waiting_for_description)
    await message.answer(
        "Qanday username kerakligini yozing.\n\n"
        "Masalan: tech, biznes, gaming, bloger yoki ismingizga mos username."
    )


@router.message(UsernameStates.waiting_for_description, F.text)
async def meaningful_username_handler(message: Message, state: FSMContext):
    try:
        usernames = await generate_codecraft_usernames(message.text)
        response = "Siz uchun ma'noli va chiroyli variantlar:\n\n"
        response += "\n".join(f"@{username}" for username in usernames)
        await message.answer(response, reply_markup=keyboard)
    except Exception:
        await message.answer(
            "Username yaratishda xatolik bo'ldi. Admin CodeCraft API keyni "
            "Secrets/environment variables ichiga qo'shganini tekshirsin."
        )
    finally:
        await state.clear()
