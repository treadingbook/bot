import os
import asyncio
import yt_dlp
import threading
from http.server import SimpleHTTPRequestHandler
import socketserver
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- ১. ডামি সার্ভার (রেন্ডারকে সচল রাখার জন্য) ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        print(f"Server online at port {port}")
        httpd.serve_forever()

# --- ২. ডাউনলোড এবং হ্যান্ডেল লজিক ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📟 CYBER BOT ONLINE!\nআপনার ভিডিও লিঙ্কটি পাঠান (সর্বোচ্চ ৫০ এমবি)।")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    status_msg = await update.message.reply_text("📡 সিগন্যাল রিসিভড... প্রসেসিং...")
    
    video_file = f"vid_{chat_id}.mp4"

    try:
        # yt-dlp সেটিংস (ইউটিউব ব্লক এড়াতে User-Agent যুক্ত)
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': video_file,
            'max_filesize': 48 * 1024 * 1024, # রেন্ডারের র‍্যাম অনুযায়ী লিমিট
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])

        await status_msg.edit_text("📤 আপলোড শুরু হচ্ছে...")
        
        with open(video_file, 'rb') as f:
            await context.bot.send_video(chat_id=chat_id, video=f, caption="✅ ডাউনলোড সম্পন্ন।")
        
        os.remove(video_file) # সার্ভার পরিষ্কার রাখা
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text("❌ এরর: লিঙ্কটি কাজ করছে না অথবা ফাইলটি অনেক বড়।")
        if os.path.exists(video_file):
            os.remove(video_file)

# --- ৩. মেইন এক্সিকিউশন ---
if __name__ == '__main__':
    # Render-এর সিক্রেটস থেকে টোকেন নেওয়া
    TOKEN = os.environ.get("BOT_TOKEN")

    if TOKEN:
        # ডামি সার্ভার ব্যাকগ্রাউন্ডে চালু করা
        threading.Thread(target=run_dummy_server, daemon=True).start()
        
        # বট চালু করা
        print("Bot is starting...")
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_video))
        app.run_polling()
