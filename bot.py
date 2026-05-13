import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
from cogs.eventos import EventoViewPersistente

# Configurar logging a archivo + consola
# Formato: 2026-05-13 13:48:34 INFO     discord.client logging in using static token
log_file = "bot.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3),
        logging.StreamHandler()
    ]
)

# Cargar variables de entorno desde .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()  # guilds, guild_messages = ON
intents.message_content = True       # comandos (!ayuda, !rank, etc.)
intents.members = True              # gestión de miembros, ranks

bot = commands.Bot(command_prefix='!', intents=intents)

# Cargar cogs
async def load_cogs():
    await bot.load_extension('cogs.ayuda')
    await bot.load_extension('cogs.baja_agente')
    await bot.load_extension('cogs.mee6')
    await bot.load_extension('cogs.permisos')
    await bot.load_extension('cogs.reload')
    await bot.load_extension('cogs.miembros')
    await bot.load_extension('cogs.temporadas')
    await bot.load_extension('cogs.rank')
    await bot.load_extension('cogs.eventos')
    await bot.load_extension('cogs.lista_espera')
    await bot.load_extension('cogs.escalation')

@bot.event
async def on_ready():
    await load_cogs()
    bot.add_view(EventoViewPersistente())
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    # Loguear error completo para debugging interno
    logging.error(f"Command '{ctx.command}' by {ctx.author} in {ctx.guild}: {error}", exc_info=True)

    # Enviar mensaje genérico al usuario (nunca mostrar detalles internos)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Faltan parámetros. Uso: `!{ctx.command.name}` — escribe `!ayuda` para ver los detalles.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes permisos para usar este comando.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ No encontré ese usuario. Asegúrate de mencionarlo con @.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Parámetro inválido. Escribe `!ayuda` para ver el uso correcto.")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignorar comandos inexistentes silenciosamente
    else:
        await ctx.send("❌ Algo salió mal. Contacta al admin.")

bot.run(TOKEN)
