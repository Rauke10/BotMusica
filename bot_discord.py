import dotenv

dotenv.load_dotenv()

class BotDiscord:
    def __init__(self):
        self.token = dotenv.get_key(dotenv.find_dotenv(), "BOT_TOKEN")
        
        
    def run(self):
        print(f"Bot is running with token: {self.token}")