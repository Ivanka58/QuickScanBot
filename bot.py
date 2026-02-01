import os
import telebot
import qrcode
from io import BytesIO
from PIL import Image
from fastapi import FastAPI
import uvicorn

# Получаем токен бота из переменных окружения Render
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Инициализируем FastAPI приложение
app = FastAPI()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Этот бот конвертирует ссылки в QR-коды.\nПросто пришли ему ссылку и он сгенерирует тебе QR-код."
    )

def generate_qr(url: str) -> bytes:
    """Генерация QR-кода по ссылке."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.read()

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

# Настройка FastAPI для прослушивания порта
@app.get("/")
async def root():
    return {"message": "Telegram QR Code Bot is running!"}

if __name__ == "__main__":
    PORT = int(os.getenv('PORT', 8080))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
