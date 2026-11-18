"""
maktuba_cakes kanal boti
Kanalga avtomatik: hol-ahvol savollari, so'rovnomalar (poll), "bugun kim qayerda" va h.k.

O'rnatish:
    pip install "python-telegram-bot[job-queue]==21.6"

Ishga tushirish:
    BOT_TOKEN=123:ABC CHANNEL=@maktuba_cakes ADMIN_ID=123456789 python maktuba_bot.py

Muhim: botni kanalga ADMIN qilib qo'shing ("Post messages" huquqi bilan).
"""
import os
import random
import logging
from datetime import time
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL = os.environ.get("CHANNEL", "@maktuba_cakes")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
TZ = ZoneInfo("Asia/Tashkent")

# ---------- KONTENT (o'zingiz tahrirlang) ----------

# Oddiy matnli postlar (hol-ahvol)
GREETINGS = [
    "☀️ Assalomu alaykum, aziz do'stlar! Bugun kayfiyatlar qalay? Izohlarda yozib qoldiring 👇",
    "🌸 Hayrli tong! Hol-ahvollaringiz yaxshimi? Bugungi rejangiz nima?",
    "☕️ Tong otdi! Kofe yoki choy — bugun nima ichyapsiz? 😄",
]

# So'rovnomalar: (savol, [variantlar])
POLLS = [
    ("🏙 Bugun qayerdasiz?", ["Toshkent", "Samarqand", "Buxoro", "Boshqa shahar", "Chet elda"]),
    ("😊 Bugungi kayfiyatingiz?", ["Zo'r 🔥", "Yaxshi 🙂", "Oddiy 😐", "Charchadim 😴"]),
    ("🎂 Eng yoqadigan tort turi?", ["Shokoladli", "Mevali", "Medovik", "Napoleon", "Bento tort"]),
    ("🍰 Shirinlik tanlang!", ["Tort", "Cheesecake", "Makaron", "Trubochka"]),
    ("🛍 Bugun nima rejangiz bor?", ["Ishga ketyapman", "O'qiyapman", "Dam olyapman", "Sayrga chiqaman"]),
    ("🎁 Tug'ilgan kunga qanday tort buyurtma qilasiz?", ["Katta (2-3 kg)", "O'rta (1-1.5 kg)", "Bento", "Kapkeyk to'plami"]),
    ("🍓 Qaysi krem yoqadi?", ["Qaymoqli", "Shokoladli", "Mevali", "Karamelli"]),
]

# "Bugun kim qayerda" — ochiq savol postlari
WHERE_TODAY = [
    "📍 Bugun kim qayerda? Shahringizni izohda yozing, ko'raylik qayerlardan ekanmiz! 🇺🇿",
    "🌍 Kanal a'zolari, bugun qayerdasiz? Uyda, ishda yoki yo'ldami? Yozing 👇",
]

# Kunlik jadval: (soat:daqiqa, tur)  tur: greeting / where / poll
SCHEDULE = [
    (time(9, 0, tzinfo=TZ), "greeting"),
    (time(12, 30, tzinfo=TZ), "where"),
    (time(18, 0, tzinfo=TZ), "poll"),
]

# ---------- FUNKSIYALAR ----------

async def send_kind(context: ContextTypes.DEFAULT_TYPE, kind: str):
    if kind == "greeting":
        await context.bot.send_message(CHANNEL, random.choice(GREETINGS))
    elif kind == "where":
        await context.bot.send_message(CHANNEL, random.choice(WHERE_TODAY))
    else:
        q, opts = random.choice(POLLS)
        await context.bot.send_poll(CHANNEL, q, opts, is_anonymous=True)


async def scheduled(context: ContextTypes.DEFAULT_TYPE):
    await send_kind(context, context.job.data)


def is_admin(update: Update) -> bool:
    return update.effective_user and update.effective_user.id == ADMIN_ID


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men maktuba_cakes kanal botiman.\n\n"
        "Admin buyruqlari:\n"
        "/hol - hol-ahvol posti\n"
        "/qayerda - 'kim qayerda' posti\n"
        "/poll - tasodifiy so'rovnoma\n"
        "/yoz matn - kanalga o'z matningizni yuborish\n"
        "/myid - Telegram ID ingiz"
    )


async def cmd_myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ID: {update.effective_user.id}")


def admin_cmd(kind):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not is_admin(update):
            return
        await send_kind(context, kind)
        await update.message.reply_text("✅ Yuborildi")
    return handler


async def cmd_write(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Foydalanish: /yoz matn")
        return
    await context.bot.send_message(CHANNEL, text)
    await update.message.reply_text("✅ Yuborildi")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(CommandHandler("hol", admin_cmd("greeting")))
    app.add_handler(CommandHandler("qayerda", admin_cmd("where")))
    app.add_handler(CommandHandler("poll", admin_cmd("poll")))
    app.add_handler(CommandHandler("yoz", cmd_write))

    for t, kind in SCHEDULE:
        app.job_queue.run_daily(scheduled, t, data=kind)

    app.run_polling()


if __name__ == "__main__":
    main()
