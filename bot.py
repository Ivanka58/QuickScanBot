import os
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pyqrcode import create as qr_create
from io import BytesIO
from PIL import Image

# Загрузка переменных окружения из .env файла
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Получаем номер порта из переменных окружения, если используется Render или аналогичный хостинг
PORT = int(os.environ.get('PORT', '80'))  # Порт указывается платформой Render

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start_handler(update: Update, context: CallbackContext):
    """Команда '/start': приветственное сообщение"""
    message = (
        "Привет! Этот бот конвертирует ссылки в QR-коды.\n"
        "Просто пришли ему ссылку и он сгенерирует тебе QR-код."
    )
    update.message.reply_text(message)

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

def link_handler(update: Update, context: CallbackContext):
    """Обработка входящих сообщений"""
    text = update.message.text.strip()
    
    if not text.startswith("http"):
        # Сообщение не является ссылкой
        reply_message = "Пришли, пожалуйста, именно ссылку!"
        update.message.reply_text(reply_message)
        return
    
    # Отправляем промежуточное сообщение о создании QR-кода
    temp_msg = update.message.reply_text("Идёт создание QR-кода...")
    
    try:
        # Генерируем QR-код
        qr_image_bytes = generate_qr(text)
        
        # Удаляем промежуточное сообщение
        context.bot.deleteMessage(chat_id=update.effective_chat.id, message_id=temp_msg.message_id)
        
        # Отправляем полученный QR-код
        update.message.reply_photo(photo=qr_image_bytes, caption=f"Ваш QR-код готов!")
        
        # Завершаем обработку сообщением благодарности
        final_message = "Спасибо за использование нашего бота!"
        update.message.reply_text(final_message)
    except Exception as e:
        print(e)
        error_message = "Что-то пошло не так при обработке вашей ссылки :("
        update.message.reply_text(error_message)

# Добавляем обработчики
dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, link_handler))

# Устанавливаем порт и начинаем работу
updater.start_polling(port=PORT)
updater.idle()
