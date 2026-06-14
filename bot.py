import requests
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # @BotFather dan
IMGBB_API_KEY = "YOUR_IMGBB_API_KEY"        # api.imgbb.com dan


# Render uchun health check
class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, *args):
        pass

def run_health():
    HTTPServer(("0.0.0.0", 8080), Health).serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom!\n\n"
        "📸 Menga rasm yuboring — men uni URL ga aylantirib beraman!\n\n"
        "Masalan: https://i.ibb.co/abc123/photo.jpg"
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Yuklanmoqda...")

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_bytes = await file.download_as_bytearray()

    response = requests.post(
        "https://api.imgbb.com/1/upload",
        params={"key": IMGBB_API_KEY},
        files={"image": ("photo.jpg", bytes(file_bytes), "image/jpeg")}
    )

    data = response.json()

    if data.get("success"):
        url = data["data"]["url"]
        await update.message.reply_text(
            f"✅ Tayyor!\n\n`{url}`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Xatolik! Qaytadan urinib ko'ring.")


async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Iltimos, faqat rasm yuboring!")


def main():
    Thread(target=run_health, daemon=True).start()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.ALL, handle_other))

    print("✅ Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
