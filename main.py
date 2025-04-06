from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp
import os
import uuid
import instaloader

# 🔑 Токен Telegram-бота
TOKEN = '8018034750:AAFbVpJCXAb_c3b5pddHJtYNkcMroxpe97c'  # заміни на свій токен

# 📥 Завантаження з YouTube
def download_youtube(url):
    filename = f"{uuid.uuid4()}.mp4"
    ydl_opts = {
        'format': 'best',
        'outtmpl': filename,
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename

# 📥 Завантаження з Instagram
def download_instagram(url):
    L = instaloader.Instaloader(download_video_thumbnails=False, quiet=True)
    post = instaloader.Post.from_shortcode(L.context, url.split("/")[-2])
    filename = f"{uuid.uuid4()}.mp4"
    L.download_post(post, target='insta_temp')
    for file in os.listdir("insta_temp"):
        if file.endswith('.mp4'):
            os.rename(f"insta_temp/{file}", filename)
            break
    return filename

# 💬 Привітання при /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли мені посилання на відео з YouTube або Instagram, і я скачаю його для тебе 📥")

# 📩 Обробка посилань
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "youtube.com" in url or "youtu.be" in url:
        await update.message.reply_text("Завантажую з YouTube...")
        video = download_youtube(url)
    elif "instagram.com" in url:
        await update.message.reply_text("Завантажую з Instagram...")
        video = download_instagram(url)
    else:
        await update.message.reply_text("Невідоме посилання, спробуй ще раз.")
        return

    await update.message.reply_video(video=open(video, 'rb'))
    os.remove(video)

# ▶️ Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущений. Чекаю повідомлень...")
    app.run_polling()
