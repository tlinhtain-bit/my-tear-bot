import logging, os, random
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- Keep Alive ---
app_flask = Flask('')
@app_flask.route('/')
def home(): return "Bot is Online"
Thread(target=lambda: app_flask.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()

# --- Config ---
TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 7771663458
CHANNEL_ID = -1003841480184

users_db = {} # {user_id: {"info": "", "photo": ""}}
context_step = {}

async def is_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, update.effective_user.id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# --- Core Logic ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    # ၁။ Forwarding System
    if update.effective_chat.type == "private" and uid != OWNER_ID:
        await context.bot.forward_message(OWNER_ID, update.effective_chat.id, update.message.message_id)
    
    # ၂။ Owner Channel Posting
    if uid == OWNER_ID and update.message.reply_to_message and "/post" in (update.message.text or ""):
        await context.bot.copy_message(CHANNEL_ID, update.effective_chat.id, update.message.reply_to_message.message_id)
        await update.message.reply_text("📢 Channel သို့ တင်ပေးလိုက်ပါပြီ။")

    # ၃။ Registration Process
    if context_step.get(uid) == "photo" and update.message.photo:
        users_db[uid] = {"photo": update.message.photo[-1].file_id}
        context_step[uid] = "info"
        await update.message.reply_text("📸 ဓာတ်ပုံရပါပြီ။ Name, Age, နေရပ်, Bio ကို ရေးပို့ပေးပါ။")
    elif context_step.get(uid) == "info" and update.message.text:
        users_db[uid]["info"] = update.message.text
        context_step[uid] = "finished"
        await update.message.reply_text("✅ မှတ်သားပြီးပါပြီ! ရည်းစားရှာရန် /find ကို နှိပ်ပါ။")

async def find_love(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    all_uids = [u for u in users_db if u != uid]
    if not all_uids:
        await update.message.reply_text("⏳ လက်ရှိ ဖူးစာရှင် ရှာမတွေ့သေးပါရှင်။")
        return
    
    target = random.choice(all_uids)
    data = users_db[target]
    kb = [[InlineKeyboardButton("✅ Love", callback_data=f"love_{target}"), InlineKeyboardButton("⏭ Skip", callback_data="find_love")]]
    await update.message.reply_photo(data['photo'], caption=f"💖 ဖူးစာရှင်အသစ်:\n{data['info']}", reply_markup=InlineKeyboardMarkup(kb))

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "find_love":
        if not await is_joined(update, context):
            await query.message.reply_text("❌ Channel ကို အရင် Join ပေးပါဦး။")
            return
        context_step[query.from_user.id] = "photo"
        await query.message.reply_text("✅ ကျေးဇူးပြု၍ ဓာတ်ပုံ ပို့ပေးပါ။")
    elif "love_" in query.data:
        await query.message.reply_text("🎉 အောင်မြင်ပါပြီ! စကားပြောလို့ရပါပြီ။")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("🎀CherryBot အသင့်ရှိပါပြီရှင့်။", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💖 ရည်းစားရှာရန်", callback_data="find_love")]]))))
    app.add_handler(CommandHandler("find", find_love))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.run_polling()

if __name__ == '__main__': main()
