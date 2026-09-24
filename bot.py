import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🤖 AI Chat", callback_data="chat"),
            InlineKeyboardButton("✍️ Text", callback_data="text"),
        ],
        [
            InlineKeyboardButton("🌐 Translate", callback_data="translate"),
            InlineKeyboardButton("🎬 YouTube", callback_data="youtube"),
        ],
        [
            InlineKeyboardButton("🏷️ Hashtag", callback_data="hashtag"),
            InlineKeyboardButton("🖼️ Image Prompt", callback_data="image_prompt"),
        ],
        [
            InlineKeyboardButton("💻 Code", callback_data="code"),
            InlineKeyboardButton("🧠 Quiz", callback_data="quiz"),
        ],
        [
            InlineKeyboardButton("🎮 Gaming Helper", callback_data="gaming"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    text = f"""
🤖 *NOVA AI*

স্বাগতম, {user.first_name}!

আমি একটি All-in-One AI Assistant।

আমি তোমাকে সাহায্য করতে পারি:

🤖 AI Chat
✍️ Text Generation
🌐 Translation
🎬 YouTube Tools
🏷️ Hashtag Generation
🖼️ Image Prompt
💻 Code Generation
🧠 Quiz
🎮 Gaming Helper

🌍 তুমি যেকোনো ভাষায় লিখতে পারো।

নিচের Menu থেকে একটি Feature নির্বাচন করো 👇
"""

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    actions = {
        "chat": "🤖 AI Chat\n\nতোমার প্রশ্নটি লিখে পাঠাও।",
        "text": "✍️ Text Generator\n\nযে ধরনের লেখা তৈরি করতে চাও সেটা লিখো।",
        "translate": "🌐 Translate\n\nযে লেখা অনুবাদ করতে চাও এবং কোন ভাষায় চাও তা লিখো।",
        "youtube": "🎬 YouTube Tools\n\nযেমন: আমার Gaming ভিডিওর জন্য একটি Title ও Description তৈরি করো।",
        "hashtag": "🏷️ Hashtag Generator\n\nতোমার ভিডিওর বিষয় লিখো।",
        "image_prompt": "🖼️ Image Prompt\n\nকী ধরনের ছবি তৈরি করতে চাও সেটা লিখো।",
        "code": "💻 Code Generator\n\nকী ধরনের code দরকার সেটা লিখো।",
        "quiz": "🧠 Quiz\n\nবিষয় লিখো। যেমন: Science, Gaming, English, History",
        "gaming": "🎮 Gaming Helper\n\nগেমের নাম এবং তোমার প্রশ্ন লিখো।",
    }

    await query.message.reply_text(actions.get(query.data, "কিছু একটা ভুল হয়েছে।"))


async def ai_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    system_prompt = """
You are NOVA AI, a multilingual all-in-one AI assistant.

The user may write in any language.
Automatically detect the user's language and normally answer in the same language.

You can help with:
- General AI chat
- Writing
- Translation
- YouTube titles and descriptions
- Hashtags
- Image prompts
- Programming
- Quizzes
- Gaming assistance

Be helpful, accurate, concise, and easy to understand.
If the user asks for code, provide complete working code when practical.
"""

    try:
        response = client.responses.create(
            model="gpt-5.6",
            instructions=system_prompt,
            input=user_text
        )

        answer = response.output_text

        await update.message.reply_text(answer)

    except Exception as e:
        logging.error(e)

        await update.message.reply_text(
            "⚠️ দুঃখিত, এখন AI response পাওয়া যাচ্ছে না। কিছুক্ষণ পরে আবার চেষ্টা করো।"
        )


def run_bot():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN পাওয়া যায়নি।")

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY পাওয়া যায়নি।")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, ai_response)
    )

    print("NOVA AI is running...")

    app.run_polling()


if __name__ == "__main__":
    run_bot()
