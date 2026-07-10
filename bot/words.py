# username generator uchun turli xil so'zlar bazasi
import random
import string

PREFIXES = ["the", "my", "top", "best", "super", "pro", "uz", "uzb", "real", "vip", "mega", "ideal", "smart", "elite"]
SUFFIXES = ["bot", "uz", "uzb", "shop", "store", "market", "biz", "pro", "tech", "dev", "app", "hub", "net", "group", "team"]

CATEGORIES = {
    "biznes": ["savdo", "biznes", "tijorat", "sotuv", "moliya", "invest", "daromad", "foyda", "bazar", "bozor", "trade", "deal", "optom", "retail"],
    "texnologiya": ["tech", "dev", "coder", "hacker", "it", "cyber", "web", "app", "soft", "code", "data", "cloud", "ai", "system"],
    "gaming": ["gamer", "play", "game", "esports", "sniper", "ninja", "pro", "noob", "win", "gg", "zone", "arena"],
    "lifestyle": ["life", "style", "auto", "sport", "news", "info", "media", "blog", "vlog", "channel", "tv"]
}

def get_all_words():
    all_words = []
    for words in CATEGORIES.values():
        all_words.extend(words)
    return all_words

def generate_smart_username():
    """Aqlli va xilma-xil usernamelar yasash algoritm"""
    all_w = get_all_words()
    word1 = random.choice(all_w)
    word2 = random.choice(all_w)
    prefix = random.choice(PREFIXES)
    suffix = random.choice(SUFFIXES)
    
    # 5 xil noyob format
    formats = [
        f"{prefix}_{word1}",                       # the_biznes
        f"{word1}_{suffix}",                       # savdo_uz
        f"{word1}{word2}",                         # techsavdo
        f"{word1}{random.randint(10, 999)}",       # bozor777
        f"{prefix}{word1}{suffix}",                # toptechuz
        f"{word1}_{random.choice(string.ascii_lowercase)}{random.randint(1, 9)}" # media_x7
    ]
    return random.choice(formats)
