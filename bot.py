import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8156834424:AAHny7W7T8fjsuIal-tNNXs8ywcLPdj5aD4"

COUNTRIES = {
    "germany": {"id": "de", "name": "Germany 🇩🇪"},
    "netherlands": {"id": "nl", "name": "Netherlands 🇳🇱"},
}

def generate_dark_tunnel_config(host, port, username, password, sni="bug.com"):
    return f"""[SSH]
Host: {host}
Port: {port}
Username: {username}
Password: {password}
SNI: {sni}
Payload: GET wss://{sni}/ HTTP/1.1[crlf]Host: {sni}[crlf]Connection: Upgrade[crlf]Upgrade: websocket[crlf][crlf]
"""

def generate_npv_config(host, port, username, password, sni="bug.com"):
    return {
        "v": 1,
        "ps": "SSHOcean",
        "add": host,
        "port": port,
        "method": "ssh",
        "user": username,
        "pass": password,
        "sni": sni,
        "proto": "ssh",
        "payload": f"GET wss://{sni}/ HTTP/1.1[crlf]Host: {sni}[crlf][crlf]",
        "tls": True
    }

async def start_ssh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(COUNTRIES["germany"]["name"], callback_data="country_germany")],
        [InlineKeyboardButton(COUNTRIES["netherlands"]["name"], callback_data="country_netherlands")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите страну сервера:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    country_key = query.data.replace("country_", "")
    if country_key not in COUNTRIES:
        await query.edit_message_text("Выбран неверный вариант.")
        return

    country = COUNTRIES[country_key]
    await query.edit_message_text(f"Генерируем SSH аккаунт для {country['name']}...")

    ssh_data = get_ssh_from_sshocean(country["id"])
    if not ssh_data:
        await query.edit_message_text("Ошибка при получении SSH аккаунта. Попробуйте позже.")
        return

    host = ssh_data["host"]
    port = ssh_data["port"]
    username = ssh_data["user"]
    password = ssh_data["pass"]

    dark_tunnel_conf = generate_dark_tunnel_config(host, port, username, password)
    npv_conf = generate_npv_config(host, port, username, password)

    text = f"""🎉 <b>SSH Account</b>:
<b>Host:</b> {host}
<b>Port:</b> {port}
<b>User:</b> {username}
<b>Password:</b> {password}

🔧 <b>Dark Tunnel Config:</b>
<pre>{dark_tunnel_conf}</pre>
"""

    # Отредактируем сообщение, чтобы показать данные
    await query.edit_message_text(text, parse_mode="HTML")

    # Сохраним npv конфиг во временный файл
    filename = f"npv_config_{query.from_user.id}.json"
    with open(filename, "w") as f:
        json.dump(npv_conf, f, indent=2)

    # Отправим файл
    await context.bot.send_document(chat_id=query.message.chat_id, document=InputFile(filename), filename="npv_config.json")

def get_ssh_from_sshocean(country_id):
    # Тут заглушка — в реальности надо парсить или использовать API SSHOcean
    try:
        url = f"https://sshocean.com/ssh-account-generator?country={country_id}"
        r = requests.get(url)
        if r.status_code != 200:
            return None
        # Пример фиктивных данных
        return {
            "host": "sg1.fastssh.com",
            "port": 443,
            "user": "user123",
            "pass": "pass123"
        }
    except Exception as e:
        print("Ошибка при получении SSH:", e)
        return None

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("ssh", start_ssh))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
