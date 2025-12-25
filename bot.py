import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

user_data = {}

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            "👋 Welcome!\n\n"
            "This group offers discounted bill payments.\n\n"
            "Type /services to begin.\n"
            "🚫 No spam allowed."
        )

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏠 Rent", callback_data="bill_Rent")],
        [InlineKeyboardButton("💡 Utilities", callback_data="bill_Utilities")],
        [InlineKeyboardButton("📱 Phone", callback_data="bill_Phone")],
        [InlineKeyboardButton("💳 Credit Card", callback_data="bill_CreditCard")],
        [InlineKeyboardButton("📄 Other", callback_data="bill_Other")]
    ]
    await update.message.reply_text("Choose bill type:", reply_markup=InlineKeyboardMarkup(keyboard))

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    user_data.setdefault(uid, {})

    if query.data.startswith("bill_"):
        user_data[uid]["bill"] = query.data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("🔁 Recurring", callback_data="type_Recurring")],
            [InlineKeyboardButton("💸 One-Time", callback_data="type_OneTime")]
        ]
        await query.edit_message_text("Payment type:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("type_"):
        user_data[uid]["ptype"] = query.data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("₿ BTC", callback_data="pay_BTC")],
            [InlineKeyboardButton("💰 PayPal", callback_data="pay_PayPal")],
            [InlineKeyboardButton("🏦 Chime", callback_data="pay_Chime")],
            [InlineKeyboardButton("🍎 Apple Pay", callback_data="pay_ApplePay")]
        ]
        await query.edit_message_text("Payment method:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("pay_"):
        user_data[uid]["method"] = query.data.split("_")[1]
        keyboard = [[InlineKeyboardButton("✅ Ready to Pay", callback_data="ready")]]
        await query.edit_message_text("When ready, tap below:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "ready":
        user = query.from_user
        info = user_data[uid]
        link = f"https://t.me/{user.username}" if user.username else "No username"

        msg = (
            "🚨 NEW REQUEST 🚨\n\n"
            f"User: {user.first_name}\n"
            f"Bill: {info['bill']}\n"
            f"Type: {info['ptype']}\n"
            f"Method: {info['method']}\n"
            f"DM: {link}"
        )

        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
        await query.edit_message_text("✅ Sent! Admin will DM you.")

async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bad = ["http", "t.me/", "free", "promo"]
    if any(x in update.message.text.lower() for x in bad):
        await update.message.delete()

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(CommandHandler("services", services))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, spam))

app.run_polling()
