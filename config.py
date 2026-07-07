import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_CHANNEL = int(os.getenv("ADMIN_CHANNEL", "0"))
PAYMENT_CARD = os.getenv("PAYMENT_CARD", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
DB_PATH = "database/saas.db"

USERNAME_PRICE = 5000  # 1 ta username narxi (so'm)
