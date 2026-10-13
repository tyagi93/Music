import os
import io
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
from google import genai
from google.genai import types
from gtts import gTTS
import pypdf

# Credentials & Admin Setup
TELEGRAM_BOT_TOKEN = "8831762730:AAFEv30ajJt9U81vmBx3BvKW5vS6STdaPOM"
GEMINI_API_KEY = "AQ.Ab8RN6J89WI3ArFpLvh7CZXUCoj0sHRWRxSkaXhQ1X8rcfNOzA"
ADMIN_ID = 8501811067
OWNER_USERNAME = "@Tyagizbg"

# AI Client Initialize
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Branding System Instructions
SYSTEM_PROMPT = (
    "Aap ek advanced aur smart AI assistant hain jise Tyagi Ji ne develop kiya hai. "
    "Kabhi bhi Google, Gemini ya kisi aur company ka naam mat lena. "
    "Jab bhi koi pooche ki kisne banaya, creator kaun hai, owner kaun hai ya 'who made you', "
    "to tumhara answer strictly exact yahi hona chahiye: 'TYAGI JI MADE THIS BOT'. "
    "Baaki sabhi sawalon ke jawab accurate, smart, helpful aur polite bhasha me dein."
)

def get_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🔍 Live Web Search", callback_data="btn_search"),
            InlineKeyboardButton("📖 Help Guide", callback_data="btn_help"),
        ],
        [
            InlineKeyboardButton("📄 PDF Summarizer", callback_data="btn_pdf"),
            InlineKeyboardButton("👑 Owner / Creator", callback_data="btn_owner"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "Dost"
    welcome_text = (
        f"👑 **NAMASTE {user_name.upper()}!** 👑\n\n"
        "✨ Main hoon aapka personal **Advanced AI Assistant**.\n"
        "⚡ Mujhse aap koi bhi sawal pooch sakte hain, live khabrein jaan sakte hain, "
        "voice me baat kar sakte hain ya documents summarize karwa sakte hain.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "👇 **Neeche diye gaye buttons se shuru karein:**"
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
            "• Main real-time internet se live information nikaal sakta hoon.\n"
            "• **Jaise:** Live match score, taaza khabrein, weather, ya latest updates.\n\n"
            "👉 Bas chat me apna sawal type karein!"
        )
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="btn_menu")]])
        await query.edit_message_text(text=text, reply_markup=back_markup, parse_mode="Markdown")

    elif query.data == "btn_help":
        text = (
            "📖 **BOT HELP & FEATURES GUIDE** 🛠️\n\n"
            "🔹 **🔍 Live Web Search:** Taaza khabrein aur real-time data search karta hai.\n"
            "🔹 **🎙️ Voice Assistant:** Audio/voice note bhejein, bot bol kar jawab dega.\n"
            "🔹 **📄 PDF Summarizer:** PDF bhejein, bot point-to-point summary bana dega.\n"
            "🔹 **👑 Owner Card:** Creator Tyagi Ji ki contact info.\n"
            "🔹 **💬 Chat:** Koi bhi sawaal type karke poochein.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ Bot hamesha aapki madad ke liye taiyar hai!"
        )
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="btn_menu")]])
        await query.edit_message_text(text=text, reply_markup=back_markup, parse_mode="Markdown")

    elif query.data == "btn_pdf":
        text = (
            "📄 **DOCUMENT / PDF SUMMARIZER** 📚\n\n"
            "• Koi bhi PDF chat me document ke roop me bhejein.\n"
            "• Bot use padh kar clean bullet points me summary dega.\n\n"
            "👉 Abhi ek PDF send karke dekhein!"
        )
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="btn_menu")]])
        await query.edit_message_text(text=text, reply_markup=back_markup, parse_mode="Markdown")

    elif query.data == "btn_owner":
        text = (
            "👑 **BOT CREATOR & ADMIN** 👑\n\n"
            "🔥 **Created By:** Tyagi Ji\n"
            "🏷️ **Tag:** `TYAGI JI MADE THIS BOT`\n"
            f"📩 **Direct Contact:** {OWNER_USERNAME}\n\n"
            "Kisi bhi madad ya custom bots ke liye directly contact karein."
        )
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="btn_menu")]])
        await query.edit_message_text(text=text, reply_markup=back_markup, parse_mode="Markdown")

    elif query.data == "btn_menu":
        welcome_text = "👑 **MAIN MENU** 👑\n\nNeeche option chunein ya direct sawal poochein:"
        await query.edit_message_text(text=welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text.strip()

    creator_keywords = ["kisne banaya", "who made", "creator", "developer", "kiska bot hai", "owner", "banaya kisne"]
    if any(k in user_prompt.lower() for k in creator_keywords):
        await update.message.reply_text("👑 TYAGI JI MADE THIS BOT")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
        )
        reply_text = response.text or "Maaf kijiye, mujhe koi uttar nahi mila."
        
        # 4096 character limit safe handling
        if len(reply_text) > 4000:
            for i in range(0, len(reply_text), 4000):
                await update.message.reply_text(reply_text[i:i+4000])
        else:
            await update.message.reply_text(reply_text)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="record_voice")

    voice_in = f"voice_{update.effective_user.id}.ogg"
    voice_out = f"reply_{update.effective_user.id}.mp3"

    try:
        voice = await update.message.voice.get_file()
        await voice.download_to_drive(voice_in)

        with open(voice_in, "rb") as f:
            audio_bytes = f.read()

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/ogg"),
                    "Is audio ka jawab dein. Agar creator ya developer ke bare me ho to strictly 'TYAGI JI MADE THIS BOT' bolna. Kisi company ka naam mat lena."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
        )

        reply_text = response.text or "Main aapki voice theek se samajh nahi paya."

        def make_tts():
            tts = gTTS(text=reply_text[:500], lang="hi")
            tts.save(voice_out)

        await loop.run_in_executor(None, make_tts)

        with open(voice_out, "rb") as v:
            await update.message.reply_voice(voice=v)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Audio error: {str(e)}")

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
        response = await loop.run_in_executor(
            None,
            lambda: ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
            )
        )

        summary_text = f"📄 **DOCUMENT SUMMARY:**\n\n{response.text}"
        if len(summary_text) > 4000:
            for i in range(0, len(summary_text), 4000):
                await update.message.reply_text(summary_text[i:i+4000])
        else:
            await update.message.reply_text(summary_text)

    except Exception as e:
        await update.message.reply_text(f"⚠️ PDF error: {str(e)}")

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

    print("Tyagi Ji Bot start ho gaya hai...")
    app.run_polling()

if __name__ == "__main__":
    main()
