import os
import google.generativeai as genai
import telebot

# Telegram Bot Token နဲ့ Gemini API Key ကို Environment Variable ကနေ ယူပါမယ်
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini API Key ကို Configuration လုပ်ခြင်း
genai.configure(api_key=GEMINI_API_KEY)

# Gemini Model ကို သတ်မှတ်ခြင်း (gemini-1.5-flash ကို သုံးထားပါတယ် - ပိုမိုတည်ငြိမ်ပါတယ်)
model = genai.GenerativeModel("gemini-1.5-flash")

# Telegram Bot စတင်ခြင်း
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# Bot ကို စတင်လိုက်တဲ့အခါ (/start)
@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(
      message,
      "မင်္ဂလာပါ! ကျွန်တော်က Gemini AI ချိတ်ထားတဲ့ Bot ပါ။ မေးချင်တာတွေကို"
      " မေးနိုင်ပါပြီ။",
  )


# စာသားများ ပို့လာပါက Gemini ဆီ ပို့ပြီး အဖြေပြန်ပေးရန်
@bot.message_handler(func=lambda message: True)
def handle_message(message):
  user_text = message.text
  try:
    response = model.generate_content(user_text)
    bot.reply_to(message, response.text)
  except Exception as e:
    bot.reply_to(message, f"မှားယွင်းမှု ရှိနေပါသည်: {str(e)}")


if __name__ == "__main__":
  print("Bot is starting...")
  bot.remove_webhook()
  bot.infinity_polling()
