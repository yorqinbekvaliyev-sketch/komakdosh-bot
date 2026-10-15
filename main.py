import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google import genai

# Токенларни сервер муҳитидан (Environment Variables) олади
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ai_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Сен ўзбек тилида равон, самимий, ақлли ва хушмуомала суҳбатдошсан. 
Фойдаланувчи қайси имлода ёзса (кирилл ёки лотин), сен ҳам айнан ўша имлода жавоб қайтар.
Таржима тилидек сунъийликдан қоч, табиий ўзбекона ибораларни ўрни билан ишлат.
Қисқа ва аниқ, керак бўлганда батафсил тушунтир.
"""

user_chats = {}

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_chats[user_id] = ai_client.chats.create(
        model="gemini-2.5-flash",
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
        )
    )
    await message.answer("Ассалому алайкум! Мен суҳбатга тайёрман. Исталган саволингизни беришингиз ёки шунчаки гаплашишимиз мумкин.")

@dp.message()
async def chat_handler(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_chats:
        user_chats[user_id] = ai_client.chats.create(
            model="gemini-2.5-flash",
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            )
        )
    
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    chat = user_chats[user_id]
    
    try:
        response = chat.send_message(message.text)
        await message.answer(response.text)
    except Exception as e:
        await message.answer("Узр, хабарни қайта ишлашда хатолик юз берди. Бироздан сўнг қайта уриниб кўринг.")
        print(f"Хатолик: {e}")

async def main():
    print("Бот муваффақиятли ишга тушди!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
