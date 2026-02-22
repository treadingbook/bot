import streamlit as st
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Streamlit UI (যাতে share.streamlit.io এটাকে অ্যাপ হিসেবে চিনে)
st.title("📟 Cyber Telegram Bot Server")
st.write("Status: [ SYSTEM ONLINE ]")
st.info("বটটি এখন ব্যাকগ্রাউন্ডে সচল আছে।")

# টেলিগ্রাম বটের কোড এখানে...
TOKEN = os.getenv('8508284133:AAHzxqRn20yIlToOnbRcl5IzYhokrj8F_0w')

async def start(update: Update, context):
    await update.message.reply_text("📟 CYBER BOT READY.")

# বটের বাকি ফাংশনগুলো আগের মতোই থাকবে...

# বট রান করার জন্য একটি বিশেষ ফাংশন (Streamlit এর জন্য)
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # ... অন্য হ্যান্ডলারগুলো ...
    
    await app.initialize()
    await app.start_polling()
    # এটি বটকে চালু রাখবে
    while True:
        await asyncio.sleep(1)

# Streamlit অ্যাপ চললে বট শুরু হবে
if TOKEN:
    try:
        asyncio.run(run_bot())
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please set BOT_TOKEN in Streamlit Secrets!")