import dotenv
from comandos import discord
from discord.ext import commands
from comandos import Comandos

dotenv.load_dotenv()

class BotDiscord:
    def __init__(self):
        self.token = dotenv.get_key(dotenv.find_dotenv(), "BOT_TOKEN")
        self.command_prefix = "!"
        # Configurar los intents
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        
        # Crear el bot con prefijo de comando
        self.bot = commands.Bot(self.command_prefix, intents=self.intents)
        
        # Evento cuando el bot está listo
        @self.bot.event
        async def on_ready():
            await self.bot.change_presence(activity=discord.Game(name="Music"))
            print(f'Conectado como {self.bot.user.name} - ID: {self.bot.user.id}')
        
        # Configurar comandos
        self.run_comandos()
        
        # Iniciar el bot automáticamente
        print("Iniciando bot...")
        self.bot.run(self.token)
        
    def run_comandos(self):
        comandos = Comandos(self.bot)
        comandos.setUp_commands()
    