import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from flask import Flask, request
import os

# --- CONFIGURATION ---
BOT_TOKEN = "8742568256:AAGcofy6BZ22gbyFHh0WbP7YRutND2D3WzM" 
ADMIN_ID = 8474225355 
# আপনার Render URL টি এখানে নিশ্চিত করুন
WEBHOOK_URL = "https://bot-es9z.onrender.com" 

# --- LOGGING SETUP ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- STATES ---
MAIN_MENU, WORK_START, IG_MOTHER_SUB, WITHDRAW_MENU = range(4)

# --- FLASK WEB SERVER FOR WEBHOOK ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    bot_app.update_queue.put(update)
    return "OK"
# --- END OF WEB SERVER ---

# --- HELPER FUNCTIONS ---
async def get_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["IG Work Start", "rules and price update"],
        ["Withdraw", "Refresh"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 মেইন মেনু:", reply_markup=reply_markup)
    return MAIN_MENU

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! আমি একটি টেলিগ্রাম বট।")
    return await get_main_menu(update, context)

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "IG Work Start":
        keyboard = [
            ["IG 2fa", "IGMother account 2fa"],
            ["IG Cookies", "Refresh"]
        ]
        await update.message.reply_text("কাজ নির্বাচন করুন:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return WORK_START
        
    elif text == "rules and price update":
        keyboard = [[InlineKeyboardButton("View Link", url="https://t.me/instafbhub/19")]]
        await update.message.reply_text("নিয়ম এবং প্রাইস আপডেট:", reply_markup=InlineKeyboardMarkup(keyboard))
        return MAIN_MENU
        
    elif text == "Withdraw":
        # সমস্যা ৫: উইথড্র বাটন কাজ করছিল না, এখন বাটন যোগ করা হয়েছে
        keyboard = [
            ["বিকাশ", "নগদ", "রকেট"],
            ["বাইনান্স", "সেভ পেমেন্ট মেথড"],
            ["Refresh"]
        ]
        await update.message.reply_text("পেমেন্ট মেথড বাছুন:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return WITHDRAW_MENU

    elif text == "Refresh":
        return await get_main_menu(update, context)
    
    return MAIN_MENU

# --- WORK START LOGIC ---
async def work_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "IG 2fa":
        await update.message.reply_text("আপনার এক্সেল ফাইলটি পাঠান")
        # সমস্যা ৩: শুধু এক্সেল ফাইল হ্যান্ডলারের জন্য ফাইল হ্যান্ডলার ফাংশন আপডেট করা হয়েছে
        
    elif text == "IGMother account 2fa":
        # সমস্যা ৪: ব্যাক করে মেন মেনুতে যাওয়া ঠিক করা হয়েছে (এখন এই স্টেটে থাকবে)
        keyboard = [["File", "Single Account"], ["Refresh"]]
        await update.message.reply_text("অপশন বাছুন (Mother Account):", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return IG_MOTHER_SUB

    elif text == "IG Cookies":
        keyboard = [[InlineKeyboardButton("File", callback_data="upload_cookies")]]
        await update.message.reply_text("কুকিজ ফাইল পাঠান:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif text == "Refresh":
        return await get_main_menu(update, context)
        
    return WORK_START

# --- ADMIN PANEL LOGIC ---
async def admin_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ আপনি এডমিন নন!")
        return
    # সমস্যা ১: ভুল টেক্সট ঠিক করা হয়েছে
    await update.message.reply_text("📊 এডমিন প্যানেল: ইউজারের তথ্য যাচাই করুন।")

async def admin_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("💰 পেমেন্ট সিস্টেম সক্রিয়।")

# --- FILE HANDLER (Excel Only) ---
async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # সমস্যা ৩: শুধু .xlsx বা .csv ফাইল সাপোর্ট করবে
    document = update.message.document
    if document.file_name.endswith(('.xlsx', '.csv', '.xls')):
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📂 নতুন এক্সেল ফাইল এসেছে ইউজার ID: {update.effective_user.id}")
        await context.bot.send_document(chat_id=ADMIN_ID, document=document.file_id)
        await update.message.reply_text("✅ ফাইলটি এডমিনের কাছে পাঠানো হয়েছে।")
    else:
        await update.message.reply_text("❌ ভুল ফাইল! শুধু এক্সেল (.xlsx, .csv) ফাইল পাঠান।")

# --- MAIN ---
if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot = bot_app.bot
    
    # হ্যান্ডলারসমূহ
    bot_app.add_handler(CommandHandler("check", admin_check))
    bot_app.add_handler(CommandHandler("payment", admin_payment))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            WORK_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, work_start_handler)],
            WITHDRAW_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            IG_MOTHER_SUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, work_start_handler)], # Fix for #4
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, start)],
    )
    
    # ফাইল হ্যান্ডলার (Excel Only)
    bot_app.add_handler(MessageHandler(filters.Document.ALL, handle_files))
    bot_app.add_handler(conv_handler)
    
    # Webhook সেটআপ
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    
    print("Bot is running with Webhook...")
    
    # Flask সার্ভার চালু
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
