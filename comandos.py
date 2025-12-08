import yt_dlp
import discord
from control_comandos import MusicControls
import re
import asyncio
from collections import deque
import os




class Comandos:
    
    
    
    def __init__(self, bot):
        self.bot = bot
        self.FFMEG_OPTIONS = {"options":"-vn","before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",}
        self.YDL_OPTS = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'verbose': False,
            'quiet': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }
        self.queue = deque()  # Cola de canciones
        self.current_song = None  # Canción actual
        self.last_url = None  # URL original de la última canción
        self.last_title = None  # Título de la última canción
        self.replay = 0  # Variable para controlar el replay
        self.music_control = None


    async def check_channel(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("¡Debes estar en un canal de voz para reproducir música!")
            return False
        
        voice_channel = ctx.author.voice.channel
        
        # Conectar al canal de voz si no está conectado
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            # Si ya está conectado, moverlo al canal del usuario
            await ctx.voice_client.move_to(voice_channel)
        
        return True
    
    
    async def skip_song(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            return True
        else:
            ctx.send('No hay música reproduciéndose para saltar')
            
    async def play_song(self, ctx, name):
        await self.check_channel(ctx)
        view = MusicControls(self, ctx)
        try:
            # Extraer información del video con yt-dlp
            with yt_dlp.YoutubeDL(self.YDL_OPTS) as ydl:
                info = ydl.extract_info(f"ytsearch1:{name}", download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                url2 = info['url']
                title = info.get('title', 'Desconocido')
                
                # Guardar URL original y título para replay
                self.last_url = name
                self.last_title = title
            
            # Crear el audio source
            source = discord.FFmpegPCMAudio(url2, **self.FFMEG_OPTIONS)
            
            # Detener cualquier reproducción actual
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            
            # Función que se ejecuta cuando termina la canción
            def after_playing(error):
                if error:
                    print(f'Error en reproducción: {error}')
                if len(self.queue) > 0:
                    asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
            
            # Reproducir la música
            if self.replay == 1:
                pass
            else:
                await ctx.send(f'🎵 Reproduciendo: **{title}**', view=view)
            ctx.voice_client.play(source, after=after_playing)
               
            
        except Exception as e:
            await ctx.send(f'❌ Error al reproducir: {str(e)}')

    async def play_next(self, ctx):
        """Reproduce la siguiente canción de la cola"""
        if len(self.queue) > 0:
            next_url = self.queue.popleft()
            print(f'Reproduciendo siguiente de la cola: {next_url}')
            await self.play_song(ctx, next_url)
        else:
            await ctx.send('✅ Cola terminada')
    
    async def add_to_queue(self, ctx, url):
        # Agregar a la cola
        self.queue.append(url)
        
        # Si no hay canción reproduciéndose, reproducir ahora
        if ctx.voice_client is None or (not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused()):
            await self.play_next(ctx)
        
        return len(self.queue)  # Retorna la posición en la cola
                
    def setUp_commands(self):
        
        
        @self.bot.command(aliases=['p'])
        async def play(ctx, *, name):
            # Verificar si el usuario está en un canal de voz
            if not await self.check_channel(ctx):
                return
            await self.play_song(ctx, name)
           

        @self.bot.command()
        async def stop(ctx):
            """Detiene la música y desconecta el bot"""
            self.queue.clear()
            self.current_song = None
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
                await ctx.send('⏹️ Reproducción detenida y desconectado')
            else:
                await ctx.send('No estoy conectado a ningún canal de voz')
        
                
        @self.bot.command(aliases=['add'])
        async def queue(ctx, *, url):
            """Agrega una canción a la cola"""
            if not ctx.voice_client or not ctx.voice_client.is_playing():
                await ctx.send('❌ Debes reproducir una canción primero')
                return
            
            # Usar la función compartida
            position = await self.add_to_queue(ctx, url)
            await ctx.send(f'➕ Canción agregada a la cola. Posición: **{position}**')
                
        @self.bot.command()
        async def skip(ctx):
            """Salta la canción actual"""
            await self.skip_song(ctx)