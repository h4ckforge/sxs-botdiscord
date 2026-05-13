import discord
from discord.ext import commands

class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reload')
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        """Recarga un cog sin reiniciar el bot.
        Uso: !reload <nombre_cog>"""
        extension = f'cogs.{cog}'
        try:
            if extension in self.bot.extensions:
                await self.bot.reload_extension(extension)
                await ctx.send(f"✅ Cog `{cog}` recargado correctamente.")
            else:
                await self.bot.load_extension(extension)
                await ctx.send(f"✅ Cog `{cog}` cargado correctamente.")
        except Exception as e:
            await ctx.send(f"❌ Error con `{cog}`: {e}")

async def setup(bot):
    await bot.add_cog(Reload(bot))
