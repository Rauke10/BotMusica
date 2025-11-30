
import os


class BotDiscord:
    def __init__(self):
        self.token = os.getenv("BOT_TOKEN")
        
    def run(self):
        print(f"Bot is running with token: {self.token}")