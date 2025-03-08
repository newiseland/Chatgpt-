import asyncio
import logging
import os
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import F

from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot token & MongoDB connection
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize bot & dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Setup MongoDB connection
client = MongoClient(MONGO_URI)
db = client["telegram_bot_db"]
collection = db["user_chats"]

# Setup OpenAI API
openai.api_key = OPENAI_API_KEY

# Logging setup
logging.basicConfig(level=logging.INFO)

# /start command handler
@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="🤖 Talk to me", callback_data="talk")
    button2 = InlineKeyboardButton(text="⚡ Features", callback_data="features")
    keyboard.add(button1, button2)

    await message.answer("Welcome! I'm an AI-powered chatbot with ChatGPT responses. 🚀", reply_markup=keyboard)

# Callback query handler
@dp.callback_query(F.data == "talk")
async def talk(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Sure! Just send me a message and I'll reply smartly. 😎")

@dp.callback_query(F.data == "features")
async def features(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "I can:\n- Chat intelligently (ChatGPT AI)\n- Store chat history\n- Be funny & sarcastic\n- Use MongoDB for memory!")

# Function to get response from ChatGPT API
async def get_chatgpt_response(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return "Sorry, I couldn't process that request. 😢"

# Message handler to store chat in MongoDB and respond using ChatGPT
@dp.message()
async def chat_response(message: types.Message):
    user_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "message": message.text
    }
    collection.insert_one(user_data)

    response = await get_chatgpt_response(message.text)
    await message.answer(response)

# Main function to run the bot
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
