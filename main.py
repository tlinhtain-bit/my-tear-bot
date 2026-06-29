import os, random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 7771663458
CHANNEL_ID = -1003841480184

users_db = {}
context_step = {}

async def start(update, context):
    kb = [[InlineKeyboardButton("💖 ရည်းစားရှာရန်", callback_data="find_love")]]
    await update.message.reply_text("🎀 cherry Bot အသင့်ရှိပါပြီ။", reply_markup=InlineKeyboardMarkup(kb))

async def handle_message(update, context):
    uid = update.effective_user.id
    # Forwarding
    if update.effective_chat.type == "private" and uid != OWNER_ID:
        await context.bot.forward_message(OWNER_ID, update.effective_chat.id, update.message.message_id)
    # Channel Posting (Owner သာ)
    if uid == OWNER_ID and update.message.reply_to_message and "/post" in (update.message.text or ""):
        await context.bot.copy_message(CHANNEL_ID, update.effective_chat.id, update.message.reply_to_message.message_id)
    
    # Register လုပ်ခြင်း
    if context_step.get(uid) == "photo" and update.message.photo:
        users_db[uid] = {"photo": update.message.photo[-1].file_id}
        context_step[uid] = "info"
        await update.message.reply_text("📸 ဓာတ်ပုံရပါပြီ။ Name, Age, နေရပ်, Bio ကို ရေးပို့ပေးပါ။")
    elif context_step.get(uid) == "info" and update.message.text:
        users_db[uid]["info"] = update.message.text
        context_step[uid] = "finished"
        await update.message.reply_text("✅ မှတ်သားပြီးပါပြီ! ဖူးစာရှင်ရှာရန် /find ကို နှိပ်ပါ။")

async def find_love(update, context):
    all_uids = [u for u in users_db if u != update.effective_user.id]
    if not all_uids: return await update.message.reply_text("⏳ ဖူးစာရှင် ရှာမတွေ့သေးပါ။")
    target = random.choice(all_uids)
    data = users_db[target]
    kb = [[InlineKeyboardButton("✅ Love", callback_data=f"love_{target}"), InlineKeyboardButton("⏭ Skip", callback_data="find_love")]]
    await update.message.reply_photo(data['photo'], caption=f"💖 ဖူးစာရှင်:\n{data['info']}", reply_markup=InlineKeyboardMarkup(kb))

async def callback(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "find_love":
        context_step[query.from_user.id] = "photo"
        await query.message.reply_text("✅ ဓာတ်ပုံ ပို့ပေးပါ။")
    elif "love_" in query.data:
        await query.message.reply_text("🎉 ချိတ်ဆက်ပေးလိုက်ပါပြီ!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find_love))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
  
