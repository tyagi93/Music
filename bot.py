import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from groq import Groq
from gtts import gTTS
import pypdf
from duckduckgo_search import DDGS

# Bot Credentials
TELEGRAM_BOT_TOKEN = "8831762730:AAFEv30ajJt9U81vmBx3BvKW5vS6STdaPOM"
GROQ_API_KEY = "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"
OWNER_USERNAME = "@Tyagizbg"

# Active standard model
MODEL_NAME = "llama-3.1-8b-instant"

# Client initialize
groq_client = Groq(api_key=GROQ_API_KEY)

# Strict branding system instruction
SYSTEM_PROMPT = (
    "Aap ek smart aur helpful AI assistant hain jise Tyagi Ji ne banaya hai. "
    "KABHI BHI kisi company, Google, Meta ya platform ka naam mat lena. "
    "Agar koi pooche 'bot kisne banaya', 'creator kaun hai', 'who made you', "
    "to saaf aur seedha jawab dein: 'Mujhe Tyagi Ji ne banaya hai'. "
    "Sabhi sawalon ke jawab clear, accurate aur polite bhasha me dein."
)

def get_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🔍 Live Web Search", callback_data="btn_search"),
            InlineKeyboardButton("📖 Help Guide", callback_data="btn_help"),
        ],
        [
            InlineKeyboardButton("📄 PDF Summarizer", callback_data="btn_pdf"),
            InlineKeyboardButton("👑 Owner Info", callback_data="btn_owner"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "Dost"
    welcome_text = (
        f"👑 **NAMASTE {user_name.upper()}!** 👑\n\n"
        "✨ Main hoon aapka personal **Advanced AI Assistant**.\n"
        "⚡ Mujhse aap sawal pooch sakte hain, live web search kar sakte hain, "
        "voice me baat kar sakte hain ya documents summarize karwa sakte hain.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "👇 **Neeche diye gaye buttons se shuru karein ya direct sawal poochein:**"
    )
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "btn_search":
        text = (
            "🔍 **LIVE WEB SEARCH MODE** 🌐\n\n"
            "• Main real-time internet se live information khoj kar bata sakta hoon.\n"
            "• **Jaise:** Live scores, taaza khabrein, weather, ya latest updates.\n\n"
            "👉 Chat me bas apna sawal type karein, bot live search karke jawab dega!"
        )
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="btn_menu")]])
        await query.edit_message_text(text=text, reply_markup=back_markup, parse_mode="Markdown")

    elif query.data == "btn_help":
        text = (
            "📖 **HELP GUIDE** 🛠️\n\n"
            "🔹 **🔍 Live Search:** Real-time web information search karta hai.\n"
            "🔹 **💬 Chat:** Normal sawal poochein, instant jawab milega.\n"
            "🔹 **🎙️ Voice Assistant:** Audio bhejoge toh bol kar reply aayega.\n"
            "🔹 **📄 PDF Summarizer:** PDF bhej kar point-to-point summary lein.\n"
            "🔹 **👑 Owner Info:** Creator contact info."
        )
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="btn_menu")]])
        await query.edit_message_text(text=text, reply_markup=back_markup, parse_mode="Markdown")

    elif query.data == "btn_pdf":
        text = (
            "📄 **DOCUMENT / PDF SUMMARIZER** 📚\n\n"
            "• Koi bhi PDF chat me document ke roop me bhejein.\n"
            "• Bot use padh kar clean points me summary nikaal dega."
        )
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="btn_menu")]])
        await query.edit_message_text(text=text, reply_markup=back_markup, parse_mode="Markdown")

    elif query.data == "btn_owner":
        text = (
            "👑 **OWNER / CREATOR INFO** 👑\n\n"
            "🔥 **Creator:** Tyagi Ji\n"
            f"📩 **Direct Contact:** {OWNER_USERNAME}"
        )
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="btn_menu")]])
        await query.edit_message_text(text=text, reply_markup=back_markup, parse_mode="Markdown")

    elif query.data == "btn_menu":
        welcome_text = "👑 **MAIN MENU**\n\nNeeche option chunein ya direct sawal poochein:"
        await query.edit_message_text(text=welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

def call_groq(prompt_text):
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_text}
        ],
        model=MODEL_NAME,
    )
    return chat_completion.choices[0].message.content

# Error-free web search function
def safe_web_search(query_text):
    try:
        results = list(DDGS().text(query_text, max_results=3))
        if results:
            lines = []
            for r in results:
                body = r.get("body", "")
                if body:
                    lines.append(body)
            return "\n".join(lines)
    except Exception:
        # Search me error aane par code crash nahi hoga
        return ""
    return ""

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text.strip()
    user_prompt_lower = user_prompt.lower()

    # Creator check
    creator_keywords = ["kisne banaya", "who made", "creator", "developer", "kiska bot hai", "owner kaun hai"]
    if any(k in user_prompt_lower for k in creator_keywords):
        await update.message.reply_text("Mujhe Tyagi Ji ne banaya hai.")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        loop = asyncio.get_running_loop()
        
        # Trigger words for live internet search
        search_triggers = ["aaj", "today", "news", "score", "price", "current", "weather", "latest", "time", "date", "match"]
        prompt_to_send = user_prompt

        if any(w in user_prompt_lower for w in search_triggers):
            web_info = await loop.run_in_executor(None, safe_web_search, user_prompt)
            if web_info:
                prompt_to_send = f"Web Real-time Data:\n{web_info}\n\nUser Question: {user_prompt}\n(Is context ke aadhar par user ko clear answer do)"

        reply_text = await loop.run_in_executor(None, call_groq, prompt_to_send)
        
        # Safe message splitting
        if len(reply_text) > 4000:
            for i in range(0, len(reply_text), 4000):
                await update.message.reply_text(reply_text[i:i+4000])
        else:
            await update.message.reply_text(reply_text)
            
    except Exception:
        # User ko ugly error screen ke badle polite message milega
        await update.message.reply_text("Maaf kijiye, abhi server se connect hone me samasya aayi. Kripya thodi der baad dobara koshish karein.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="record_voice")

    voice_in = f"voice_{update.effective_user.id}.ogg"
    voice_out = f"reply_{update.effective_user.id}.mp3"

    try:
        voice = await update.message.voice.get_file()
        await voice.download_to_drive(voice_in)

        loop = asyncio.get_running_loop()
        def transcribe():
            with open(voice_in, "rb") as file:
                return groq_client.audio.transcriptions.create(
                    file=(voice_in, file.read()),
                    model="whisper-large-v3",
                ).text

        transcribed_text = await loop.run_in_executor(None, transcribe)

        creator_keywords = ["kisne banaya", "who made", "creator", "developer", "kiska bot hai"]
        if any(k in transcribed_text.lower() for k in creator_keywords):
            reply_text = "Mujhe Tyagi Ji ne banaya hai."
        else:
            reply_text = await loop.run_in_executor(None, call_groq, transcribed_text)

        def make_tts():
            tts = gTTS(text=reply_text[:500], lang="hi")
            tts.save(voice_out)

        await loop.run_in_executor(None, make_tts)

        with open(voice_out, "rb") as v:
            await update.message.reply_voice(voice=v)

    except Exception:
        await update.message.reply_text("Voice samajhne me dikkat aayi, kripya dobara voice note bhejein.")

    finally:
        for p in [voice_in, voice_out]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not (document.file_name and document.file_name.lower().endswith(".pdf")):
        await update.message.reply_text("⚠️ Kripya sirf PDF file bhejein.")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    pdf_path = f"doc_{update.effective_user.id}.pdf"

    try:
        tg_file = await document.get_file()
        await tg_file.download_to_drive(pdf_path)

        reader = pypdf.PdfReader(pdf_path)
        extracted_text = ""
        for page in reader.pages[:15]:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

        if not extracted_text.strip():
            await update.message.reply_text("⚠️ Is PDF se text read nahi ho saka.")
            return

        prompt = (
            "Neeche diye gaye document ko clean bullet points me summarize karo:\n\n"
            + extracted_text[:10000]
        )

        loop = asyncio.get_running_loop()
        summary = await loop.run_in_executor(None, call_groq, prompt)

        summary_text = f"📄 **DOCUMENT SUMMARY:**\n\n{summary}"
        if len(summary_text) > 4000:
            for i in range(0, len(summary_text), 4000):
                await update.message.reply_text(summary_text[i:i+4000])
        else:
            await update.message.reply_text(summary_text)

    except Exception:
        await update.message.reply_text("PDF read karne me samasya aayi. Kripya dusri PDF bhejein.")

    finally:
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception:
                pass

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
        
