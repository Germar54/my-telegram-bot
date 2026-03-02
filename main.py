import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from flask import Flask
import threading

# --- CONFIGURATION ---
# আপনার টোকেন এবং আইডি এখানে বসানো হয়েছে
BOT_TOKEN = "8535441292:AAGbaOFGoMdXbh36w1IPwFBMvsymI__iOi4" 
ADMIN_ID = 8474225355 
MIN_WITHDRAW = 50

# --- LOGGING SETUP ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- STATES ---
MAIN_MENU, WORK_START, IG_MOTHER_SUB, WITHDRAW_MENU = range(4)

# --- FLASK WEB SERVER FOR RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_webserver():
    # Render-এর জন্য ১০০০০ পোর্ট ব্যবহার করা নিরাপদ
    app.run(host='0.0.0.0', port=10000)
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
        await update.message.reply_text("হাই", reply_markup=InlineKeyboardMarkup(keyboard))
        return MAIN_MENU
        
    elif text == "Withdraw":
        keyboard = [
            ["বিকাশ", "নগদ", "রকেট"],
            ["বাইনান্স", "সেভ পেমেন্ট মেথড"],
            ["Refresh"]
        ]
        await update.message.reply_text("মেথড বাছুন:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return WITHDRAW_MENU

    elif text == "Refresh":
        return await get_main_menu(update, context)
    
    return MAIN_MENU

# --- WORK START LOGIC ---
async def work_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "IG 2fa":
        await update.message.reply_text("আপনার এক্সেল ফাইলটি পাঠান")
        
    elif text == "IGMother account 2fa":
        keyboard = [["File", "Single Account"], ["Refresh"]]
        await update.message.reply_text("অপশন বাছুন:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return IG_MOTHER_SUB

    elif text == "IG Cookies":
        keyboard = [[InlineKeyboardButton("File", callback_data="upload_cookies")]]
        await update.message.reply_text("https://t.me/instafbhub/42", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif text == "Refresh":
        return await get_main_menu(update, context)
        
    return WORK_START

# --- ADMIN PANEL LOGIC ---
async def admin_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ আপনি এডমিন নন!")
        return
    await update.message.reply_text("📊 ইউজারের তথ্য পাঠানো হয়েছে (কোড লজিক লাগবে)")

async def admin_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("💰 ব্যালেন্স এডিট করা হয়েছে।")

# --- FILE HANDLER (For Admin) ---
async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    document = update.message.document
    
    # ফাইল এডমিনকে পাঠানোর লজিক
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"📂 নতুন ফাইল ইউজার ID: {user.id}")
    await context.bot.send_document(chat_id=ADMIN_ID, document=document.file_id)
    await update.message.reply_text("✅ ফাইল এডমিনের কাছে পাঠানো হয়েছে।")

# --- MAIN ---
if __name__ == '__main__':
    # Flask ওয়েব সার্ভার থ্রেড চালু করুন
    t = threading.Thread(target=run_webserver)
    t.start()
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # এডমিন হ্যান্ডলারসমূহ
    application.add_handler(CommandHandler("check", admin_check))
    application.add_handler(CommandHandler("payment", admin_payment))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            WORK_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, work_start_handler)],
            WITHDRAW_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, start)],
    )
    
    # ফাইল হ্যান্ডলার
    application.add_handler(MessageHandler(filters.Document.ALL, handle_files))
    application.add_handler(conv_handler)
    
    print("Bot is running...")
    # Polling চালু করুন
    application.run_polling()
    
