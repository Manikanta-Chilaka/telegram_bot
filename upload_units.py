import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("BOT_TOKEN")
BASE_DIR = "notes"
PORT = int(os.environ.get("PORT", 10000))  # For Render.com compatibility

# PDF Structure (organized by subject)
PDF_MAPPING = {
    "Computer Networks": {
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
    # Add more subjects here as needed
}

class BotHandlers:
    @staticmethod
    async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show main menu with subjects"""
        keyboard = [
            [InlineKeyboardButton(subject, callback_data=f"subject_{subject}")]
            for subject in PDF_MAPPING.keys()
        ]
        
        if update.message:
            await update.message.reply_text(
                "📚 Select a subject:",
                reply_markup=InlineKeyboardMarkup(keyboard)
        else:
            await update.callback_query.edit_message_text(
                "📚 Select a subject:",
                reply_markup=InlineKeyboardMarkup(keyboard))

    @staticmethod
    async def handle_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show PDF options for selected subject"""
        query = update.callback_query
        await query.answer()
        
        subject = query.data.replace("subject_", "")
        if subject not in PDF_MAPPING:
            await query.edit_message_text("Subject not found!")
            return

        buttons = []
        for cmd, filename in PDF_MAPPING[subject].items():
            # Format button text (remove prefix and clean up)
            btn_text = cmd.replace(subject.lower().replace(" ", ""), "") \
                         .replace("_", " ") \
                         .title()
            buttons.append([InlineKeyboardButton(btn_text, callback_data=f"send_{subject}_{cmd}")])

        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")])
        
        await query.edit_message_text(
            f"📂 Available files for {subject}:",
            reply_markup=InlineKeyboardMarkup(buttons)
    
    @staticmethod
    async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send the requested PDF"""
        query = update.callback_query
        await query.answer()
        
        _, subject, cmd = query.data.split("_", 2)
        if subject not in PDF_MAPPING or cmd not in PDF_MAPPING[subject]:
            await query.message.reply_text("Invalid selection!")
            return
            
        filename = PDF_MAPPING[subject][cmd]
        file_path = os.path.join(BASE_DIR, subject, filename)
        
        try:
            with open(file_path, "rb") as file:
                await query.message.reply_document(
                    document=file,
                    caption=f"📄 {filename}"
                )
        except FileNotFoundError:
            await query.message.reply_text("⚠️ File not found on server!")
            logger.error(f"File not found: {file_path}")
        except Exception as e:
            await query.message.reply_text("⚠️ Error sending file!")
            logger.error(f"Error sending file: {e}")

def setup_handlers(application: Application) -> None:
    """Register all handlers"""
    handlers = [
        CommandHandler("start", BotHandlers.menu),
        CommandHandler("menu", BotHandlers.menu),
        CallbackQueryHandler(BotHandlers.handle_subject, pattern="^subject_"),
        CallbackQueryHandler(BotHandlers.handle_pdf, pattern="^send_"),
        CallbackQueryHandler(BotHandlers.menu, pattern="^back_to_menu$"),
    ]
    
    for handler in handlers:
        application.add_handler(handler)

def run_bot() -> None:
    """Run the bot with polling"""
    application = Application.builder().token(TOKEN).build()
    setup_handlers(application)
    
    logger.info("Starting bot in polling mode...")
    application.run_polling()

def run_web_server() -> None:
    """Dummy web server for Render.com compatibility"""
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Telegram bot is running in background"
    
    import threading
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': PORT}).start()

if __name__ == "__main__":
    # Start dummy web server if running on Render
    if os.getenv("RENDER"):
        run_web_server()
    
    # Start the bot
    run_bot()
