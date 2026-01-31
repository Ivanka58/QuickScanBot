import os
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pyqrcode import create as qr_create
from io import BytesIO
from PIL import Image

# Загрузка переменных окружения из .env файла
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

application = ApplicationBuilder().token(TOKEN).build()

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда '/start': приветственное сообщение"""
    message = (
        "Привет! Этот бот конвертирует ссылки в QR-коды.\\n"
        "Просто пришли ему ссылку и он сгенерирует тебе QR-код."
    )
    await update.message.reply_text(message)

def generate_qr(url: str) -> bytes:
    """Генерация QR-кода по ссылке"""
    qr_code = qr_create(url)
    buffer = BytesIO()
    qr_code.png(buffer, scale=6)
    buffer.seek(0)
    img = Image.open(buffer)
    new_buffer = BytesIO()
    img.save(new_buffer, format="PNG")
    new_buffer.seek(0)
    return new_buffer.read()

async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка входящих сообщений"""
    text = update.message.text.strip()
    
    if not text.startswith("http"):
        # Сообщение не является ссылкой
        reply_message = "Пришли, пожалуйста, именно ссылку!"
        await update.message.reply_text(reply_message)
        return
    
    # Отправляем промежуточное сообщение о создании QR-кода
    temp_msg = await update.message.reply_text("Идёт создание QR-кода...")
    
    try:
        # Генерируем QR-код
        qr_image_bytes = generate_qr(text)
        
        # Удаляем промежуточное сообщение
        await context.bot.deleteMessage(chat_id=update.effective_chat.id, message_id=temp_msg.message_id)
        
        # Отправляем полученный QR-код
        await update.message.reply_photo(photo=qr_image_bytes, caption=f"Ваш QR-код готов!")
        
        # Завершаем обработку сообщением благодарности
        final_message = "Спасибо за использование нашего бота!"
        await update.message.reply_text(final_message)
    except Exception as e:
        print(e)
        error_message = "Что-то пошло не так при обработке вашей ссылки :("
        await update.message.reply_text(error_message)

# Добавляем обработчики
application.add_handler(CommandHandler('start', start_handler))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), link_handler))

# Запускаем бота
application.run_polling()
