from telegram import TelegramBot
from os import environ as env
from ngrok import Ngrok
from totp import TOTP
import subprocess
import requests
import time
import os

def check_connection():
    try:
        requests.get("https://1.1.1.1/")
        return True
    except:
        return False

while not check_connection(): time.sleep(1)

hostname = env["HOSTNAME"]
target_ip = env.get("DESTINATION", subprocess.getoutput("ip route | grep default").split()[2])
ngrok = Ngrok("./ngrok." + env["ARCH"], env["NGROK_TOKEN"], env["PROTOCOL"], target_ip, int(env["PORT"]), env["REGION"])
totp = TOTP(env["TOTP_SECRET"]) if env.get("TOTP_SECRET") else None
bot_owner = int(env["TELEGRAM_BOT_OWNER"])

expecting_authentication = False

def on_update(bot, update):
    global expecting_authentication

    message = update["message"]
    if message["from"]["id"] != bot_owner or message["chat"]["id"] != bot_owner or message["chat"]["type"] != "private":
        return
    
    text = message["text"]
    chat = message["chat"]["id"]
    if expecting_authentication:
        if totp is None or totp.verify(text):
            ip = ngrok.start()
            bot.send_message(chat, f"Ngrok instance has been started.\nPort {ngrok.port} of {hostname} is now available at {ip}")
        else:
            bot.send_message(chat, "Wrong totp code.\nNgrok instance has not been started")
        expecting_authentication = False
    else:
        if text == "/start":
            if ngrok.is_running():
                bot.send_message(chat, f"Ngrok is already running and available at {ngrok.get_public_url()}")
            else:
                bot.send_message(chat, "To start the ngrok instance, please enter your totp code:")
                expecting_authentication = True
        elif text == "/stop":
            if ngrok.is_running():
                ngrok.stop()
                bot.send_message(chat, "The ngrok instance has been stopped.")
            else:
                bot.send_message(chat, "Ngrok is not running.")

if env.get("TELEGRAM_BOT_TOKEN"):
    telegram_bot = TelegramBot(env["TELEGRAM_BOT_TOKEN"])
    telegram_bot.send_message(bot_owner, f"{hostname} is now up and running. Type /start to forward port {ngrok.port} via ngrok.")
    telegram_bot.run(on_update)
else:
    print(ngrok.start())
    while True:
        time.sleep(1)
