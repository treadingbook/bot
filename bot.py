import os
import asyncio
import yt_dlp
import threading
from http.server import SimpleHTTPRequestHandler
import socketserver
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- ১. ডামি সার্ভার (Render-এর স্লিপ মোড এড়ানোর জন্য) ---
def run_dummy_server():
    # Render অটোমেটিক একটি PORT এনভায়রনমেন্ট ভেরিয়েবল দেয়
    port = int(os.environ.get("PORT", 8080))
    handler = SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Server alive on port {port}")
        httpd.serve_forever()

# --- ২. ডাউনলোড ফাংশন (সব প্ল্যাটফর্মের জন্য) ---
async def download_video(url, video_file):
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # MP4 ফরম্যাট নিশ্চিত করতে
        'outtmpl': video_file,
        'max_filesize': 48 * 1024 * 1024, # টেলিগ্রামের ৫০ এমবি লিমিটের নিচে রাখা
        'quiet': True,
        'no_warnings': True,
        # ব্রাউজারের মতো আচরণ করতে User-Agent যোগ করা
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        await asyncio.to_thread(ydl.download, [url])

# --- ৩. বট হ্যান্ডেলার ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📟 CYBER BOT ONLINE!\nআপনার ভিডিও লিঙ্কটি পাঠান। (সর্বোচ্চ ৫০ এমবি)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    # লিঙ্ক কি না চেক করা
    if not url.startswith("http"):
        return

    status_msg = await update.message.reply_text("📡 সিগন্যাল রিসিভড... প্রসেসিং...")
    video_file = f"video_{chat_id}.mp4"

    try:
        await download_video(url, video_file)
        await status_msg.edit_text("📤 আপলোড শুরু হচ্ছে...")
        
        with open(video_file, 'rb') as f:
            await context.bot.send_video(
                chat_id=chat_id, 
                video=f, 
                caption="✅ মিশন সাকসেসফুল।",
                connect_timeout=60 # বড় ফাইলের জন্য সময় বাড়ানো
            )
        
        # ক্লিনআপ
        os.remove(video_file)
        await status_msg.delete()

    except Exception as e:
        error_text = str(e)
        if "File is too large" in error_text or "max_filesize" in error_text:
            await status_msg.edit_text("❌ ফাইলটি অনেক বড়! ৫০ এমবি-র নিচের ভিডিও দিন।")
        else:
            await status_msg.edit_text(f"❌ এরর: লিঙ্কটি কাজ করছে না। (Platform Blocked or Invalid Link)")
        
        if os.path.exists(video_file):
            os.remove(video_file)

# --- ৪. মেইন রানার ---
if __name__ == '__main__':
    # Render Secrets থেকে টোকেন নেওয়া
    TOKEN = os.environ.get("BOT_TOKEN")
    
    if TOKEN:
        # ডামি সার্ভার চালু করা (Background Thread)
        threading.Thread(target=run_dummy_server, daemon=True).start()
        
        # বট চালু করা
        print("Bot is booting up...")
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        app.run_polling()
    else:
        print("⚠️ BOT_TOKEN পাওয়া যায়নি!")
