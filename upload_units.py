from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
TOKEN = os.getenv("BOT_TOKEN")

BASE_DIR = "notes"

# PDF Structure (modify as needed)
PDF_MAPPING = {
    "cnunit1": ("Computer Networks", "Unit-1.pdf"),
    "cnunit2": ("Computer Networks", "CN Unit-2.pdf"),
    "cnunit3_part1": ("Computer Networks", "CN Unit-3 Part1.pdf"),
    "cnunit3_part2": ("Computer Networks", "CN Unit-3 Part-2.pdf"),
    "cnunit4": ("Computer Networks", "CN Unit-4.pdf"),
    "cnunit5": ("Computer Networks", "CN Unit-5.pdf"),
    "cnunit6": ("Computer Networks", "CN Unit-6.pdf"),
    "cntextbook": ("Computer Networks", "CN textbook.pdf"),
    "cnonlinenotes": ("Computer Networks", "CN Online notes.pdf")
}


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu with subjects"""
    keyboard = [
        [InlineKeyboardButton("📚 Computer Networks", callback_data="subject_cn")]
        # Add more subjects here if needed
    ]
    await update.message.reply_text(
        "Select a subject:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show PDF options for selected subject"""
    query = update.callback_query
    await query.answer()  # Important: acknowledge the callback

    # Create PDF buttons
    buttons = []
    for cmd, (subject, filename) in PDF_MAPPING.items():
        # Format button text nicely (remove 'cn' and underscores)
        btn_text = cmd.replace("cn", "").replace("_", " ").title()
        buttons.append([InlineKeyboardButton(btn_text, callback_data=f"send_{cmd}")])

    # Add back button
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")])

    await query.edit_message_text(
        "📂 Available Files:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the requested PDF"""
    query = update.callback_query
    await query.answer()  # Remove loading indicator

    cmd = query.data.replace("send_", "")
    if cmd in PDF_MAPPING:
        subject, filename = PDF_MAPPING[cmd]
        file_path = os.path.join(BASE_DIR, subject, filename)

        if os.path.exists(file_path):
            await query.message.reply_document(
                document=open(file_path, "rb"),
                caption=f"Here's {filename}"
            )
        else:
            await query.message.reply_text("⚠️ File not found!")
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
    app.add_handler(CommandHandler("menu", menu))

    # Callback handlers
    app.add_handler(CallbackQueryHandler(handle_subject, pattern="^subject_"))
    app.add_handler(CallbackQueryHandler(handle_pdf, pattern="^send_"))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))

    app.run_polling()


if __name__ == "__main__":
    main()
