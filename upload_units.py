import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
BASE_DIR = "notes"

# PDF Structure (all files directly in notes folder)
PDF_MAPPING = {
    "cnunit1": "Unit-1.pdf",
    "cnunit2": "CN Unit-2.pdf",
    "cnunit3_part1": "CN Unit-3 Part1.pdf",
    "cnunit3_part2": "CN Unit-3 Part-2.pdf",
    "cnunit4": "CN Unit-4.pdf",
    "cnunit5": "CN Unit-5.pdf",
    "cnunit6": "CN Unit-6.pdf",
    "cntextbook": "CN textbook.pdf",
    "cnonlinenotes": "CN Online notes.pdf"
}

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu with subjects"""
    keyboard = [
        [InlineKeyboardButton("📚 Computer Networks", callback_data="subject_cn")]
    ]
    await update.message.reply_text(
        "Select a subject:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show PDF options for selected subject"""
    query = update.callback_query
    await query.answer()

    buttons = []
    for cmd, filename in PDF_MAPPING.items():
        btn_text = cmd.replace("cn", "").replace("_", " ").title()
        buttons.append([InlineKeyboardButton(btn_text, callback_data=f"send_{cmd}")])

    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")])

    await query.edit_message_text(
        "📂 Available Files:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the requested PDF"""
    query = update.callback_query
    await query.answer()

    cmd = query.data.replace("send_", "")
    if cmd in PDF_MAPPING:
        filename = PDF_MAPPING[cmd]
        file_path = os.path.join(BASE_DIR, filename)

        try:
            with open(file_path, 'rb') as file:
                await query.message.reply_document(
                    document=file,
                    caption=f"Here's {filename}"
                )
        except FileNotFoundError:
            await query.message.reply_text("⚠️ File not found!")
            logger.error(f"File not found: {file_path}")
        except Exception as e:
            await query.message.reply_text("⚠️ Error sending file!")
            logger.error(f"Error sending file: {e}")
    else:
        await query.message.reply_text("Invalid selection")

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    query = update.callback_query
    await query.answer()
    await menu(query.message, context)

def main():
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", menu))
    app.add_handler(CommandHandler("menu", menu))

    # Callback handlers
    app.add_handler(CallbackQueryHandler(handle_subject, pattern="^subject_"))
    app.add_handler(CallbackQueryHandler(handle_pdf, pattern="^send_"))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))

    # For Render.com compatibility - FIXED PARENTHESES HERE
    if os.getenv('RENDER'):
        from flask import Flask
        import threading
        
        flask_app = Flask(__name__)
        
        @flask_app.route('/')
        def home():
            return "Telegram bot is running"
        
        # Fixed the parentheses closure here
        flask_thread = threading.Thread(
            target=lambda: flask_app.run(
                host='0.0.0.0',
                port=int(os.environ.get('PORT', 10000))
        )
        flask_thread.start()

    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
