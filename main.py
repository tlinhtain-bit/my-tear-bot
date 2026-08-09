import os
import threading
import flask
import google.generativeai as genai
import telebot
from PIL import Image
from io import BytesIO

# --- Configuration ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
system_instruction = "မင်းဟာ ဒီ Telegram bot ကို သုံးတဲ့သူရဲ့ အခင်ဆုံး သူငယ်ချင်း ဖြစ်တယ်။ နွေးထွေးတယ်၊ ကြင်နာတယ်၊ စာနာတတ်တယ်။ ရင်းနှီးတဲ့ အသံနဲ့ ပြောပါ။"
text_model = genai.GenerativeModel(model_name="gemini-3.6-flash", system_instruction=system_instruction)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = flask.Flask(__name__)

# --- Ping Server (UptimeRobot အတွက်) ---
@app.route('/')
def index():
    return "Bot is alive!"

def run_server():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# --- Bot Logic ---
user_states = {}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "ဟိုင်း! ငါရောက်လာပြီ။ မင်းနဲ့ စကားပြောဖို့ စောင့်နေတာ။")

@bot.message_handler(func=lambda message: message.text.lower() == "ပုံဆွဲပေးပါ")
def ask_for_prompt(message):
    user_states[message.chat.id] = "waiting_for_prompt"
    bot.reply_to(message, "ချစ်တို့ရေ.. ဘယ်လိုပုံလေး ဆွဲပေးရမလဲ? အသေးစိတ် ပြောပြပေးပါဦးနော်။")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "waiting_for_prompt")
def generate_image(message):
    prompt = message.text
    user_states[message.chat.id] = None
    bot.reply_to(message, "အိုကေ.. ခဏလေး ဆွဲပေးမယ်နော်။")
    try:
        result = genai.generate_images(prompt=prompt, model="imagen-3.0-generate-002", number_of_images=1)
        for image in result.generated_images:
            image_data = Image.open(BytesIO(image.image.image_bytes))
            bot.send_photo(message.chat.id, image_data)
    except Exception as e:
        bot.reply_to(message, "အဆင်မပြေဖြစ်သွားတယ်.. နောက်တစ်ခါ ထပ်စမ်းကြည့်ပေးပါလား။")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        response = text_model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "တစ်ခုခုတော့ မှားသွားပြီ.. ငါ့ကို ပြန်ပြောပြပေးပါလား။")

# --- Run ---
if __name__ == "__main__":
    bot.remove_webhook()
    # Server ကို Thread တစ်ခုအနေနဲ့ အရင် Run
    threading.Thread(target=run_server).start()
    # Bot ကို Polling ဆက်လုပ်
    bot.infinity_polling()
