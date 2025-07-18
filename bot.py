import telebot
import time
import json

TOKEN = '7904713151:AAFeLmjtQm8_1KEKrcpjyaX36ZHVHDuijMU'  # Вставь сюда свой токен
bot = telebot.TeleBot(TOKEN)

ssh_list = [
    {"host": "sg1.fastssh.com", "port": "443", "username": "user1", "password": "pass1", "expires": "7 дней"},
    {"host": "jp1.fastssh.com", "port": "443", "username": "user2", "password": "pass2", "expires": "7 дней"},
    {"host": "us1.fastssh.com", "port": "443", "username": "user3", "password": "pass3", "expires": "7 дней"},
]

history_file = "ssh_history.json"

try:
    with open(history_file, "r") as f:
        user_history = json.load(f)
except:
    user_history = {}

def save_history():
    with open(history_file, "w") as f:
        json.dump(user_history, f)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Напиши /getssh, чтобы получить SSH аккаунт (до 3 раз в день).")

@bot.message_handler(commands=['getssh'])
def getssh(message):
    user_id = str(message.from_user.id)
    today = time.strftime("%Y-%m-%d")

    if user_id in user_history:
        counts = user_history[user_id].get(today, 0)
        if counts >= 3:
            bot.send_message(message.chat.id, "⚠️ Вы уже получили 3 аккаунта сегодня. Приходите завтра.")
            return
    else:
        user_history[user_id] = {}

    if not ssh_list:
        bot.send_message(message.chat.id, "❌ Нет доступных аккаунтов. Попробуйте позже.")
        return

    acc = ssh_list.pop(0)
    user_history[user_id][today] = user_history[user_id].get(today, 0) + 1
    save_history()

    text = f"""✅ Ваш SSH аккаунт:
Host: {acc['host']}
Port: {acc['port']}
Username: {acc['username']}
Password: {acc['password']}
Срок: {acc['expires']}
"""
    bot.send_message(message.chat.id, text)

print("Бот запущен. Ожидание сообщений...")
bot.polling()
