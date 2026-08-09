import os
from google import genai
import telebot

# Telegram Bot Token နဲ့ Gemini API Key ကို Environment Variable ကနေ ယူပါမယ်
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Bot နှင့် Gemini ကို စတင်ချိတ်ဆက်ခြင်း
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)


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
    # လက်ရှိ အသုံးအများဆုံးနဲ့ အလုပ်လုပ်မယ့် Model (gemini-2.5-flash) ကို သုံးထားပါတယ်
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_text,
    )
    bot.reply_to(message, response.text)
  except Exception as e:
    # တစ်စုံတစ်ရာ Error တက်ခဲ့ရင် အကြောင်းရင်းကို ပို့ပေးပါမယ်
    bot.reply_to(message, f"မှားယွင်းမှု ရှိနေပါသည်: {str(e)}")


if __name__ == "__main__":
  print("Bot is starting...")
  # ယခင် Webhook ရှိနေပါက ဖယ်ရှားပေးခြင်း
  bot.remove_webhook()

  # Bot ကို စတင် Run ခြင်း
  bot.infinity_polling()
