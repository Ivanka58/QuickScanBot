import os
import telebot
from pyqrcode import create as qr_create
from io import BytesIO
from PIL import Image

# Получаем токен бота из переменных окружения Render
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Этот бот конвертирует ссылки в QR-коды.\\nПросто пришли ему ссылку и он сгенерирует тебе QR-код."
    )

def generate_qr(url: str) -> bytes:
    """Генерация QR-кода по ссылке."""
    qr_code = qr_create(url)
    buffer = BytesIO()
    qr_code.png(buffer, scale=6)
    buffer.seek(0)
    img = Image.open(buffer)
    new_buffer = BytesIO()
    img.save(new_buffer, format="PNG")
    new_buffer.seek(0)
    return new_buffer.read()

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    text = message.text.strip()
    
    if not text.startswith("http"):
        # Сообщение не является ссылкой
        bot.reply_to(message, "Пришли, пожалуйста, именно ссылку!")
        return
    
    # Отправляем промежуточное сообщение о создании QR-кода
    temp_msg = bot.send_message(message.chat.id, "Идёт создание QR-кода...")
    
    try:
        # Генерируем QR-код
        qr_image_bytes = generate_qr(text)
        
        # Удаляем промежуточное сообщение
        bot.delete_message(temp_msg.chat.id, temp_msg.message_id)
        
        # Отправляем полученный QR-код
        bot.send_photo(message.chat.id, photo=qr_image_bytes, caption="Ваш QR-код готов!")
        
        # Завершаем обработку сообщением благодарности
        bot.send_message(message.chat.id, "Спасибо за использование нашего бота!")
    except Exception as e:
        print(e)
        bot.reply_to(message, "Что-то пошло не так при обработке вашей ссылки :(")

# Запускаем бота
bot.infinity_polling()
