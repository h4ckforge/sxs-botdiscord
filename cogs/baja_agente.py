import discord
from discord.ext import commands

MENSAJE_BAJA = """Hola agente, te escribimos desde Sangre x Sangre.

Hemos notado que llevas un tiempo sin actividad en el clan y vamos a proceder a darte de baja para mantener el espacio activo.

Si en algún momento quieres volver, las puertas están abiertas. Entra al Discord a <#1352780158926323752>

🩸 Sangre x Sangre"""

class BajaAgente(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='baja-agente')
    @commands.is_owner()
    async def baja_agente(self, ctx, *usuarios: discord.Member):
        """Envía un mensaje de baja por MD a uno o más usuarios.
        Uso: !baja-agente @usuario1 [@usuario2 ...]"""
        if not usuarios:
            await ctx.send("❌ Debes mencionar al menos un usuario. Uso: `!baja-agente @usuario1 @usuario2`")
            return

        resultados = []
        for usuario in usuarios:
            try:
                await usuario.send(MENSAJE_BAJA)
                resultados.append(f"✅ MD enviado a {usuario.display_name}")
            except discord.Forbidden:
                resultados.append(f"⚠️ No se pudo enviar MD a {usuario.display_name} (tiene los MD cerrados)")
            except Exception as e:
                resultados.append(f"❌ Error con {usuario.display_name}: {str(e)}")

        await ctx.send("\n".join(resultados))

async def setup(bot):
    await bot.add_cog(BajaAgente(bot))
