import requests
import time
import json


class TelegramBot:
    def __init__(self, token):
        self.token = token
        assert self.check_token(), "Invalid token!"
        self.username = self.get_me()["username"]
        self.last_update = -1
        self.get_updates()

    def command(self, cmd, **kwargs):
        try:
            return requests.post("https://api.telegram.org/bot" + self.token + "/" + cmd, kwargs).json()
        except:
            return {"ok": False}

    def run(self, on_update, interval=1):
        print("bot '%s' is running" % self.username)
        try:
            while True:
                for u in self.get_updates():
                    on_update(self, u)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nBye.")

    def send_message(self, chat_id, text):
        self.command("sendMessage", chat_id=chat_id, text=text)

    def get_updates(self):
        updates = self.command("getUpdates", offset=self.last_update+1)
        if not updates["ok"]:
            return []
        out = [u for u in updates["result"] if u["update_id"] > self.last_update]
        if out:
            self.last_update = out[-1]["update_id"]
        return out

    def get_me(self):
        return self.command("getMe")["result"]

    def check_token(self):
        return self.command("getMe")["ok"]
