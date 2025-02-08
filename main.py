import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Load environment variables from .env file (your token)
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TOKEN is None:
    raise ValueError("⚠️ ERROR: Token not found. Make sure you have created a .env file with TELEGRAM_BOT_TOKEN.")

# Conversation states
BALANCE, INTEREST_RATE, TIME = range(3)

# Bot functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your initial balance:")
    return BALANCE

async def get_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        balance = float(update.message.text)
        if balance < 0:
            await update.message.reply_text("Balance cannot be negative. Try again:")
            return BALANCE
        context.user_data['balance'] = balance
        await update.message.reply_text("Enter the interest rate (%):")
        return INTEREST_RATE
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a number:")
        return BALANCE

async def get_interest_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        interest_rate = float(update.message.text)
        if interest_rate < 0:
            await update.message.reply_text("Interest rate cannot be negative. Try again:")
            return INTEREST_RATE
        context.user_data['interest_rate'] = interest_rate
        await update.message.reply_text("Enter the period in years:")
        return TIME
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a number:")
        return INTEREST_RATE

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        time = int(update.message.text)
        if time < 0:
            await update.message.reply_text("Time cannot be negative. Try again:")
            return TIME

        balance = context.user_data['balance']
        interest_rate = context.user_data['interest_rate']
        final_amount = balance * pow((1 + interest_rate / 100), time)

        await update.message.reply_text(
            f"**Final result after {time} years** 💰\n"
            f"Final amount: €{final_amount:,.2f}"
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter an integer:")
        return TIME

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation canceled.")
    return ConversationHandler.END


# configuration and launch

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BALANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_balance)],
            INTEREST_RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_interest_rate)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
