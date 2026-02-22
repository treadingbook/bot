import os
import asyncio
import yt_dlp
import threading
from http.server import SimpleHTTPRequestHandler
import socketserver
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- ১. ডামি সার্ভার (রেন্ডারের ফ্রি টায়ার সচল রাখার জন্য) ---
def run_dummy_server():
    # রেন্ডার অটোমেটিক একটি PORT এনভায়রনমেন্ট ভেরিয়েবল দেয়
    port = int(os.environ.get("PORT", 8080))
    handler = SimpleHTTPRequestHandler
    # এটি একটি সিম্পল এইচটিটিপি সার্ভার চালু করবে
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Dummy server running on port {port}")
        httpd.serve_forever()

# --- ২. টেলিগ্রাম বট লজিক ---
# এটি আপনার Render Environment Variables থেকে টোকেন নেবে
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📟 CYBER BOT ONLINE (RENDER).\nযেকোনো ভিডিও লিঙ্ক পাঠান, আমি ডাউনলোড করছি।")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    msg = await update.message.reply_text("📡 সিগন্যাল রিসিভড... প্রসেসিং...")
    
    video_file = f"vid_{chat_id}.mp4"

    try:
        # yt-dlp কনফিগারেশন
        ydl_opts = {
            'format': 'best',
            'outtmpl': video_file,
            'max_filesize': 48 * 1024 * 1024 # রেন্ডারের মেমরি ও টেলিগ্রাম লিমিট মাথায় রেখে
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])

        await msg.edit_text("📤 আপলোড করা হচ্ছে...")
        
        with open(video_file, 'rb') as f:
            await context.bot.send_video(chat_id=chat_id, video=f, caption="✅ মিশন সাকসেসফুল।")
        
        # পাঠানোর পর ফাইল ডিলিট করা
        os.remove(video_file)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ এরর: লিঙ্কটি কাজ করছে না অথবা ফাইলটি অনেক বড়।")
        if os.path.exists(video_file):
            os.remove(video_file)

# --- ৩. মেইন এক্সিকিউশন ---
if __name__ == '__main__':
    if not TOKEN:
        print("Error: BOT_TOKEN not found in environment variables!")
    else:
        # ডামি সার্ভারকে আলাদা থ্রেডে চালানো যাতে বট ব্লক না হয়
        threading.Thread(target=run_dummy_server, daemon=True).start()
        
        # টেলিগ্রাম বট স্টার্ট করা
        print("Bot is starting...")
        app = ApplicationBuilder().token(TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_video))
        
        app.run_polling()
