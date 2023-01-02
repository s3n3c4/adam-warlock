import telebot

ApiKey = "5418394136:AAG0ogP4l3Se3rN7PFObtRZeBQUUOmvEisg"

bot = telebot.TeleBot(ApiKey)

@bot.message_handler(content_types=[
    "new_chat_members"
])
def send_message(message:str):    
    user_first_name = str(message.from_user.first_name)
    bot.reply_to(message, "Olá " + user_first_name + """ tudo bom? sou o MoradorBot;
        Por questões de segurança e principalmente para a socialização e identificar novos vizinhos, aqueles que entram no grupo precisam se apresentar informando: 
        - Nome;  
        - Apartamento;  
        - Fase (Formosa, Mauá, Cais);  
        Estamos no aguardo! 
        
        P.S: Quem estiver mentindo na compra do RW ou se tiver dificuldade em ler o contrato, melhor não entrar , pois ficará marcado em vermelho na planilha
        Caso você já tenha se apresentado e esteja devidamente registrado(a) na planilha, favor, desconsiderar a mensagem!!
        Obrigado!
        """)

@bot.message_handler(commands=["planilha"])
def planilha(msg):
    bot.send_message(msg.chat.id, "https://docs.google.com/spreadsheets/d/1dHDLR-Z8OFkHO_pQ6NFR3IhB3IezJKmg0p4JaNqRn0Y/edit?usp=sharing")

@bot.message_handler(commands=["riowonderdecor"])
def riowonderdecor(msg):
    bot.send_message(msg.chat.id, "https://chat.whatsapp.com/JCIaQ65tz8JJxAPmHSfCbe")

@bot.message_handler(commands=["instagram"])
def instagram(msg):
    bot.send_message(msg.chat.id, "https://www.instagram.com/rio.wonder.compradores/")

@bot.message_handler(commands=["riowondersemfiltro"])
def riowondersemfiltro(msg):
    bot.send_message(msg.chat.id, "https://chat.whatsapp.com/JvviqEADHvr6cSAt2jKf5d")

@bot.message_handler(commands=["whatsapp"])
def whatsapp(msg):
    bot.send_message(msg.chat.id, "https://chat.whatsapp.com/HaVa1gkhtyx1DR4YJTjO8J")

@bot.message_handler(commands=["facebook"])
def facebook(msg):
    bot.send_message(msg.chat.id, "https://www.facebook.com/groups/riowonderresidences")

@bot.message_handler(commands=["youtube"])
def youtube(msg):
    bot.send_message(msg.chat.id, "https://www.youtube.com/channel/UCXM_R-BgEunXbV3yrih44dA/featured")
    

def Check(msg):
    return True

@bot.message_handler(commands=["ajuda"])
def answer(msg):
    txt = """

❗ Clique na opção desejada:

➡ /planilha
➡ /riowonderdecor
➡ /riowondersemfiltro
➡ /instagram
➡ /whatsapp
➡ /facebook
"""
    bot.reply_to(msg, txt)

bot.polling()