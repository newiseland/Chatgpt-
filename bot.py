import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize bot and dispatcher
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Setup MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["telegram_bot_db"]
collection = db["user_chats"]

# Logging setup
logging.basicConfig(level=logging.INFO)

# /start command handler
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("🤖 Talk to me", callback_data="talk")
    button2 = types.InlineKeyboardButton("⚡ Features", callback_data="features")
    keyboard.add(button1, button2)
    await message.reply("Welcome! I'm an AI-powered chatbot. Let's have some fun! 🚀", reply_markup=keyboard)

# Callback query handler
@dp.callback_query_handler(lambda c: c.data == "talk")
async def talk(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Sure! Just send me a message and I'll respond smartly. 😎")

@dp.callback_query_handler(lambda c: c.data == "features")
async def features(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "I can:\n- Chat intelligently\n- Store chat history\n- Be funny & sarcastic\n- Use MongoDB for memory!")

# Message handler to store chat in MongoDB and respond smartly
@dp.message_handler()
async def chat_response(message: types.Message):
    user_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "message": message.text
    }
    collection.insert_one(user_data)
    response = f"You said: {message.text} 🤖 (I'll improve with time!)"
    await message.reply(response)

# Run bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
