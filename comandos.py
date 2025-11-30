import yt_dlp
import discord
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
        self.rept_url = None  # URL de la canción actual para repetir
        


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
    
    
    async def play_song(self, ctx, url):
        await self.check_channel(ctx)
        try:
            # Extraer información del video con yt-dlp
            with yt_dlp.YoutubeDL(self.YDL_OPTS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                self.rept_url = info['url']
                title = info.get('title', 'Desconocido')
            
            # Crear el audio source
            source = discord.FFmpegPCMAudio(url2, **self.FFMEG_OPTIONS)
            
            # Detener cualquier reproducción actual
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            
            # Reproducir la música
            ctx.voice_client.play(source)
            await ctx.send(f'🎵 Reproduciendo: **{title}**')
            
        except Exception as e:
            await ctx.send(f'❌ Error al reproducir: {str(e)}')


                
    def setUp_commands(self):
        
        
        @self.bot.command()
        async def play(ctx, *, url):
            # Verificar si el usuario está en un canal de voz
            if not await self.check_channel(ctx):
                return
            await self.play_song(ctx, url)
           

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
        
        
        @self.bot.command()
        async def pause(ctx):
            """Pausa la reproducción"""
            if ctx.voice_client and ctx.voice_client.is_playing():
                ctx.voice_client.pause()
                await ctx.send('⏸️ Música pausada')
            else:
                await ctx.send('No hay música reproduciéndose')
        
        @self.bot.command()
        async def resume(ctx):
            """Reanuda la reproducción"""
            if ctx.voice_client and ctx.voice_client.is_paused():
                ctx.voice_client.resume()
                await ctx.send('▶️ Música reanudada')
            else:
                await ctx.send('La música no está pausada')
        
        
        @self.bot.command()
        async def repetir(ctx):
            if self.rept_url:
                await self.play_song(ctx, self.rept_url)
                await ctx.send(f'🎵 Reproduciendo: **{self.rept_url}**')
            else:
                await ctx.send('No hay canción para repetir')