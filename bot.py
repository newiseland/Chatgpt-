import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot token & MongoDB connection
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# Initialize bot & dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Setup MongoDB connection
client = MongoClient(MONGO_URI)
db = client["telegram_bot_db"]
collection = db["user_chats"]

# Logging setup
logging.basicConfig(level=logging.INFO)

# /start command handler
@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="🤖 Talk to me", callback_data="talk")
    button2 = InlineKeyboardButton(text="⚡ Features", callback_data="features")
    keyboard.add(button1, button2)

    await message.answer("Welcome! I'm an AI-powered chatbot. Let's have some fun! 🚀", reply_markup=keyboard)

# Callback query handler
@dp.callback_query(lambda c: c.data == "talk")
async def talk(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Sure! Just send me a message and I'll respond smartly. 😎")

@dp.callback_query(lambda c: c.data == "features")
async def features(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "I can:\n- Chat intelligently\n- Store chat history\n- Be funny & sarcastic\n- Use MongoDB for memory!")

# Message handler to store chat in MongoDB and respond smartly
@dp.message()
async def chat_response(message: types.Message):
    user_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "message": message.text
    }
    collection.insert_one(user_data)

    response = f"You said: {message.text} 🤖 (I'll improve with time!)"
    await message.answer(response)

# Main function to run the bot
async def main():
    dp.include_router(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
