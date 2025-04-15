import os
import uuid
import shutil
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp
import instaloader

# 🔐 Отримання токена з змінного середовища
TOKEN = os.getenv("TOKEN")  # Перевір, щоб у .env або середовищі була ця змінна

# 📥 Завантаження з YouTube
def download_youtube(url):
    filename = f"{uuid.uuid4()}.mp4"
    ydl_opts = {
        'format': 'best',
        'outtmpl': filename,
        'quiet': True,
        'noplaylist': True,
        'max_filesize': 50 * 1024 * 1024  # 50 MB ліміт
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename

# 📥 Завантаження з Instagram
def download_instagram(url):
    shortcode = url.rstrip("/").split("/")[-1]
    L = instaloader.Instaloader(download_video_thumbnails=False, quiet=True)
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    temp_dir = "insta_temp"
    os.makedirs(temp_dir, exist_ok=True)
    L.download_post(post, target=temp_dir)

    filename = f"{uuid.uuid4()}.mp4"
    for file in os.listdir(temp_dir):
        if file.endswith(".mp4"):
            os.rename(f"{temp_dir}/{file}", filename)
            break

    shutil.rmtree(temp_dir, ignore_errors=True)
    return filename

# 👋 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Надішли мені посилання на відео з YouTube або Instagram, і я скачаю його для тебе 📥"
    )

# 📩 Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    try:
        if "youtube.com" in url or "youtu.be" in url:
            await update.message.reply_text("🔄 Завантажую з YouTube...")
            video = download_youtube(url)
        elif "instagram.com" in url:
            await update.message.reply_text("🔄 Завантажую з Instagram...")
            video = download_instagram(url)
        else:
            await update.message.reply_text("🚫 Невідоме посилання. Надішли посилання з YouTube або Instagram.")
            return

        await update.message.reply_video(video=open(video, 'rb'))
        os.remove(video)

    except Exception as e:
        await update.message.reply_text(f"❌ Сталася помилка при завантаженні відео.\n{str(e)}")

# ▶️ Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущений. Чекаю повідомлень...")
    app.run_polling()
