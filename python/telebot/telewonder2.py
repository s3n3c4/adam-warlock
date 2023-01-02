import telebot

ApiKey = "5418394136:AAG0ogP4l3Se3rN7PFObtRZeBQUUOmvEisg"

bot = telebot.TeleBot(ApiKey)

def send_message_to_private(chat_id, text):
    api = f'https://api.telegram.org/bot5418394136:AAG0ogP4l3Se3rN7PFObtRZeBQUUOmvEisg/sendMessage?chat_id=-1001191250306&text="Qualquercoias"'
    #response = requests.get(api).json()
    #eturn  response
