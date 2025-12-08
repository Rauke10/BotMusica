import discord

class AddToQueueModal(discord.ui.Modal, title='Añadir a la Cola'):
    # Definir el campo de texto como atributo de clase
    cancion = discord.ui.TextInput(
        label='Canción',
        placeholder='Nombre o URL de la canción...',
        style=discord.TextStyle.short,
        required=True,
        max_length=200
    )
    
    def __init__(self, comandos, ctx):
        super().__init__()
        self.comandos = comandos
        self.ctx = ctx
    
    # Método que se ejecuta cuando el usuario envía el formulario
    async def on_submit(self, interaction: discord.Interaction):
        position = await self.comandos.add_to_queue(self.ctx, str(self.cancion.value))
        await interaction.response.send_message(
            f'➕ **{self.cancion.value}** agregada a la cola. Posición: **{position}**',
            ephemeral=False
        )

        

class MusicControls(discord.ui.View):
    def __init__(self, comandos,ctx):
        super().__init__(timeout=None)
        self.comandos = comandos
        self.ctx = ctx
    
    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.primary)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Usa el mismo código que tu comando pause
        if self.ctx.voice_client and self.ctx.voice_client.is_playing():
            self.ctx.voice_client.pause()
            await interaction.response.defer()
            #await interaction.followup.send('⏸️ Música pausada', ephemeral=False)
        else:
            await interaction.response.defer()
            #await interaction.followup.send('❌ No hay música reproduciéndose', ephemeral=True)
            
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.success)
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Usa el mismo código que tu comando resume
        if self.ctx.voice_client and self.ctx.voice_client.is_paused():
            self.ctx.voice_client.resume()
            await interaction.response.defer()
            #await interaction.followup.send('▶️ Música reanudada', ephemeral=False)
        else:
            await interaction.response.defer()
            #await interaction.followup.send('❌ La música no está pausada', ephemeral=True)
    
    @discord.ui.button(label="➕", style=discord.ButtonStyle.secondary)
    async def add_queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddToQueueModal(self.comandos, self.ctx)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        song_skipped = await self.comandos.skip_song(self.ctx)
        if song_skipped:
            await interaction.response.defer()
            #await interaction.followup.send('⏭️ Canción saltada', ephemeral=False)
        else:
            await interaction.response.defer()
            #await interaction.followup.send('❌ No hay música reproduciéndose para saltar', ephemeral=True)