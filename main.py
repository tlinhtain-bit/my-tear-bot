import os
import google.generativeai as genai
import telebot

# Telegram Bot Token နဲ့ Gemini API Key ကို Environment Variable ကနေ ယူပါမယ်
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini API Key ချိတ်ဆက်ခြင်း
genai.configure(api_key=GEMINI_API_KEY)

# ပုံထဲကအတိုင်း gemini-3.6-flash ကို တိုက်ရိုက်သုံးထားပါတယ်
model = genai.GenerativeModel("gemini-3.6-flash")

# Telegram Bot စတင်ခြင်း
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(
      message, "မင်္ဂလာပါ! Gemini 3.6 Flash Bot အဆင်သင့် ဖြစ်ပါပြီ။"
  )


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
