import streamlit as st
import os
import asyncio
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# পেজ সেটআপ
st.set_page_config(page_title="Cyber Telegram Server", page_icon="📟")
st.title("📟 Cyber Telegram Bot Server")

# টোকেন চেক করা (Streamlit Secrets থেকে নেবে)
TOKEN = st.secrets.get("8508284133:AAHzxqRn20yIlToOnbRcl5IzYhokrj8F_0w")

if not TOKEN:
    st.error("⚠️ BOT_TOKEN পাওয়া যায়নি! দয়া করে Streamlit Secrets-এ টোকেন সেট করুন।")
    st.stop()

st.success("✅ সিস্টেম অনলাইন! বট এখন মেসেজ রিসিভ করতে পারবে।")
st.info("আপনার টেলিগ্রাম অ্যাপে গিয়ে বটটি টেস্ট করুন।")

# বটের ফাংশনসমূহ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📟 CYBER BOT READY.\nলিঙ্ক পাঠান, আমি ডাউনলোড করছি।")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    msg = await update.message.reply_text("📡 প্রসেসিং...")
    
    video_fn = f"vid_{chat_id}.mp4"
    try:
        ydl_opts = {'format': 'best', 'outtmpl': video_fn, 'max_filesize': 50*1024*1024}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        with open(video_fn, 'rb') as f:
            await context.bot.send_video(chat_id=chat_id, video=f)
        os.remove(video_fn)
    except Exception as e:
        await msg.edit_text(f"❌ এরর: {str(e)[:50]}")

# বট রান করার মেইন ফাংশন
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_video))
    
    await app.initialize()
    await app.start_polling()
    while True:
        await asyncio.sleep(1)

# Streamlit-এ বটটি ব্যাকগ্রাউন্ডে চালানোর ট্রিক
if st.button("RESTART BOT"):
    st.rerun()

try:
    asyncio.run(main())
except Exception as e:
    st.warning("বটটি ব্যাকগ্রাউন্ডে চলছে...")

