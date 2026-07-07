import os

with open("bot/payments.py", "w", encoding="utf-8") as f:
    f.write("""from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import PAYMENT_CARD, ADMIN_CHANNEL
import aiosqlite
from config import DB_PATH

router = Router()

@router.message(F.photo)
async def handle_payment_receipt(message: Message):
    # Agar foydalanuvchi rasm tashlasa (chek), adminga yuboramiz
    caption = f"💰 Yangi to'lov cheki!\nFoydalanuvchi: {message.from_user.id}\nSummani tasdiqlang:"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ 50,000 so'm", callback_data=f"approve_{message.from_user.id}_50000")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{message.from_user.id}")]
    ])
    
    await message.bot.send_photo(
        chat_id=ADMIN_CHANNEL, 
        photo=message.photo[-1].file_id, 
        caption=caption, 
        reply_markup=markup
    )
    await message.answer("✅ Chek adminga yuborildi. Tasdiqlangach, balansingizga pul tushadi.")

@router.callback_query(F.data.startswith("approve_"))
async def approve_payment(call: CallbackQuery):
    _, user_id, amount = call.data.split("_")
    user_id = int(user_id)
    amount = int(amount)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE telegram_id = ?", (amount, user_id))
        await db.commit()
        
    await call.message.edit_caption(caption=f"✅ To'lov tasdiqlandi. ({amount} so'm tushirildi).")
    await call.bot.send_message(chat_id=user_id, text=f"🎉 Balansingiz {amount} so'mga to'ldirildi!")
""")

with open("worker/sniper.py", "w", encoding="utf-8") as f:
    f.write("""import asyncio
import logging
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UsernameOccupiedError, UsernameInvalidError
from telethon.tl.functions.account import CheckUsernameRequest
from telethon.tl.functions.channels import CreateChannelRequest, UpdateUsernameRequest
from telethon.sessions import StringSession
import aiosqlite
from config import API_ID, API_HASH, DB_PATH
from worker.generator import generate_usernames

logger = logging.getLogger(__name__)

async def process_order(order_id: int, telegram_id: int, category: str, quantity: int, session_string: str):
    client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
    await client.connect()
    
    if not await client.is_user_authorized():
        logger.error(f"User {telegram_id} session is invalid.")
        return
        
    targets = generate_usernames(category, limit=quantity * 10)
    found = 0
    
    for username in targets:
        if found >= quantity:
            break
            
        try:
            is_available = await client(CheckUsernameRequest(username=username))
            if is_available:
                new_channel = await client(CreateChannelRequest(
                    title=username.capitalize(),
                    about="Band qilindi",
                    megagroup=False
                ))
                channel_id = new_channel.chats[0].id
                
                await client(UpdateUsernameRequest(
                    channel=channel_id,
                    username=username
                ))
                
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute("INSERT INTO registered_usernames (order_id, username) VALUES (?, ?)", (order_id, username))
                    await db.execute("UPDATE orders SET registered_count = registered_count + 1 WHERE id = ?", (order_id,))
                    await db.commit()
                
                found += 1
                logger.info(f"✅ Band qilindi: @{username}")
                
            await asyncio.sleep(1) # Delay against flood wait
            
        except FloodWaitError as e:
            logger.warning(f"FloodWait: Sleeping for {e.seconds}s")
            await asyncio.sleep(e.seconds)
        except UsernameOccupiedError:
            pass
        except UsernameInvalidError:
            pass
        except Exception as e:
            logger.error(f"Error checking {username}: {e}")
            await asyncio.sleep(2)
            
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = 'completed' WHERE id = ?", (order_id,))
        await db.commit()
        
    await client.disconnect()
""")

print("Phase 2 files created")
