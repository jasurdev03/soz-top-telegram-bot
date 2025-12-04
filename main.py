import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "Your_telegrambot_token"

bot = Bot(TOKEN)
dp = Dispatcher()

# Davlatlar ro'yxati
from baza import words  # sizning words ro'yxatingiz (256 ta davlat)

users = {}

def hide_word(word, opened):
    return " ".join([ch if ch in opened else "_" for ch in word])

def start_game(user_id):
    word = random.choice(words).upper()
    users[user_id] = {
        "word": word,
        "opened": [],
        "tries": 0
    }
    return hide_word(word, [])

def guess_input(user_id, text):
    text = text.upper()
    if user_id not in users:
        return None, "O‘yin boshlanmagan! /play bilan boshlang."

    data = users[user_id]
    word = data["word"]
    data["tries"] += 1

    # Foydalanuvchi butun so'zni topgan bo'lsa
    if text == word:
        tries = data["tries"]
        del users[user_id]
        return word, f"🎉 TOPDINGIZ! {tries} TA URUNISHDA.\nYana o‘ynash uchun /play bosing."

    # Bitta harf yoki substring bo'yicha yangilash
    updated = False
    for ch in text:
        if ch in word and ch not in data["opened"]:
            data["opened"].append(ch)
            updated = True

    hidden = hide_word(word, data["opened"])

    # Agar hamma harflar ochilgan bo'lsa
    if "_" not in hidden:
        tries = data["tries"]
        del users[user_id]
        return hidden, f"🎉 TOPDINGIZ! {tries} TA URUNISHDA.\nYana o‘ynash uchun /play bosing."

    # Agar foydalanuvchi yuborgan harflar so‘zda yo‘q bo‘lsa
    if not updated:
        return hidden, "BU HARF YOKI QISM SO‘ZDA YO‘Q!"

    return hidden, None

# =========================
# Handlers
# =========================

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    await msg.answer(
        "DAVLAT NOMI YASHIRINGAN. Har bir harf yoki davlat nomining qismini kiriting.\n"
        "O‘yin boshlash uchun /play buyrug‘ini bosing."
    )

@dp.message(Command("play"))
async def cmd_play(msg: types.Message):
    user_id = msg.from_user.id
    hidden = start_game(user_id)
    await msg.answer(f"Yangi o‘yin boshlandi!\n\n{hidden}\n\nHarf yoki davlat nomining qismini yuboring:")

@dp.message()
async def handle_input(msg: types.Message):
    user_id = msg.from_user.id
    text = msg.text.strip()

    hidden, info = guess_input(user_id, text)
    if hidden is None:
        await msg.answer(info)
        return

    await msg.answer(hidden)
    if info:
        await msg.answer(info)

# =========================
# Start bot
# =========================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

