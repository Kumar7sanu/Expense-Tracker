import json
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import db
import parser
import export


# ---------------------------------
# Load Config
# ---------------------------------

with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

TOKEN = CONFIG["telegram_token"]
CURRENCY = CONFIG["currency"]


# ---------------------------------
# Helpers
# ---------------------------------

def current_date():

    now = datetime.now()

    return {
        "date": now.strftime("%Y-%m-%d"),
        "month": now.strftime("%Y-%m"),
        "weekday": now.strftime("%A")
    }


# ---------------------------------
# Commands
# ---------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = f"""
👋 Welcome to {CONFIG["dashboardTitle"]}

Simply send transactions like:

• Swiggy 420 dinner
• Uber airport 650
• Blinkit 1500 groceries
• Salary 75000

Commands

/total
/budget
/recent
/stats
/undo
/help
"""

    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await start(update, context)


async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):

    income = db.total_income()
    expense = db.total_expense()
    savings = income - expense

    msg = f"""
📊 Overall Summary

Income : {CURRENCY}{income:,.2f}

Expense : {CURRENCY}{expense:,.2f}

Savings : {CURRENCY}{savings:,.2f}
"""

    await update.message.reply_text(msg)


async def budget(update: Update, context: ContextTypes.DEFAULT_TYPE):

    expense = db.total_expense()

    budget = CONFIG["monthlyBudget"]

    left = budget - expense

    used = (expense / budget * 100) if budget else 0

    msg = f"""
💰 Budget

Budget : {CURRENCY}{budget:,.2f}

Spent : {CURRENCY}{expense:,.2f}

Remaining : {CURRENCY}{left:,.2f}

Used : {used:.1f}%
"""

    await update.message.reply_text(msg)


async def recent(update: Update, context: ContextTypes.DEFAULT_TYPE):

    rows = db.recent(5)

    if not rows:

        await update.message.reply_text("No transactions found.")

        return

    msg = "🧾 Recent Transactions\n\n"

    for row in rows:

        sign = "+" if row["type"] == "income" else "-"

        msg += (
            f"{sign} {CURRENCY}{row['amount']:,.2f} | "
            f"{row['merchant']} | "
            f"{row['category']}\n"
        )

    await update.message.reply_text(msg)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cats = db.category_summary()

    if not cats:

        await update.message.reply_text("No expense data available.")

        return

    msg = "📈 Category Summary\n\n"

    for row in cats:

        msg += f"{row['category']} : {CURRENCY}{row['total']:,.2f}\n"

    await update.message.reply_text(msg)


async def undo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    success = db.undo_last(update.effective_chat.id)

    if success:

        export.export()

        await update.message.reply_text("✅ Last transaction removed.")

    else:

        await update.message.reply_text("Nothing to undo.")


# ---------------------------------
# Message Handler
# ---------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        parsed = parser.parse_message(update.message.text)

        d = current_date()

        db.add_transaction(

            date=d["date"],

            month=d["month"],

            weekday=d["weekday"],

            merchant=parsed["merchant"],

            category=parsed["category"],

            amount=parsed["amount"],

            note=parsed["note"],

            txn_type=parsed["type"],

            chat_id=update.effective_chat.id

        )

        export.export()

        sign = "💰 Income" if parsed["type"] == "income" else "💸 Expense"

        reply = f"""
✅ Saved Successfully

{sign}

Amount : {CURRENCY}{parsed["amount"]:,.2f}

Merchant : {parsed["merchant"]}

Category : {parsed["category"]}

Note : {parsed["note"]}
"""

        await update.message.reply_text(reply)

    except Exception as e:

        await update.message.reply_text(f"❌ {str(e)}")


# ---------------------------------
# Main
# ---------------------------------

def main():

    db.init_db()

    export.export()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("budget", budget))
    app.add_handler(CommandHandler("recent", recent))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("undo", undo))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("🚀 Expense Tracker Bot Started...")

    app.run_polling()


if __name__ == "__main__":
    main()