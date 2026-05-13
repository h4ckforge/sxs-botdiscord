import discord
from discord.ext import commands

class Mee6(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='new')
    async def cmd_new(self, ctx):
        """Muestra recursos para nuevos agentes.
        Uso: !new"""
        pass

    @commands.command(name='primera-raid')
    async def cmd_primera_raid(self, ctx):
        """Requisitos y qué esperar en tu primera raid en Sangre x Sangre.
        Uso: !primera-raid"""
        mensaje = (
            "⚔️ **¿Tu primera raid en Sangre x Sangre?**\n\n"
            "Todos pasamos por esto y la hermandad está aquí para acompañarte. "
            "Solo pedimos dos cosas para empezar:\n\n"
            "\u2022 Tener un build similar a los de <#1484646681571102881>\n"
            "\u2022 Tener micrófono y/o disposición de comunicarse\n\n"
            "Esto es lo mínimo para que puedas participar y que la raid fluya bien para todos. "
            "También puedes pedir rol a los agentes con más experiencia durante la raid, no tengas miedo de preguntar.\n\n"
            "**Después de tu primera raid:**\n"
            "\u2022 Revisa <#1361058159170420928> y <#1360812497531047946> para ver los builds que usan los demás\n"
            "\u2022 Pregunta cómo y por qué se usan en los canales de voz o en <#1310374234127732826>\n\n"
            "🩸 *Mientras más builds manejes, más roles puedes cubrir y más divertida se vuelve para todos.*"
        )
        await ctx.send(mensaje)

    @commands.command(name='test')
    async def cmd_test(self, ctx):
        """test.
        Uso: !test"""
        pass

    @commands.command(name='raid')
    async def cmd_raid(self, ctx):
        """Explica cómo unirse a una raid en Sangre x Sangre.
        Uso: !raid"""
        mensaje = (
            "🎯 **¿Cómo unirte a una Raid en Sangre x Sangre?**\n\n"
            "Las raids se organizan de varias formas:\n\n"
            "🔴 **Raids improvisadas** — Un agente abre grupo y busca compañeros en el momento. "
            "Estate atento al canal de tu plataforma y súmate cuando veas una:\n"
            "🖥️ PC → <#1356052786617254071>\n"
            "🎮 PS → <#1483584379107283106>\n"
            "🟢 Xbox → <#1483589315677257818>\n\n"
            "📅 **Raids programadas** — Las encontrarás en la sección **EVENTOS**, visible en la parte superior "
            "de la lista de canales. Ahí se publican con fecha, hora y plataforma. "
            "Solo confirma tu participación antes de que se llene el grupo.\n\n"
            "🎙️ **Micrófono** — No es obligatorio, pero se agradece.\n\n"
            "⚔️ **¿Primera raid?** — Revisa `!primera-raid` antes de entrar para saber qué se espera de tu build.\n\n"
            "🩸 *Nadie nace sabiendo. Todos los agentes de Sangre x Sangre están dispuestos a ayudar, "
            "pero también esperamos que pongas tu parte.*"
        )
        await ctx.send(mensaje)

    @commands.command(name='plataformas')
    async def cmd_plataformas(self, ctx):
        """Muestra las plataformas disponibles en Sangre x Sangre y a quién contactar.
        Uso: !plataformas"""
        mensaje = (
            "```\n"
            "SANGRE X SANGRE — PLATAFORMAS\n"
            "```\n"
            "🖥️ **PC**\n"
            "Contacta a <@584876785133682688> para unirte al clan en PC.\n\n"
            "🎮 **PlayStation**\n"
            "Contacta a <@1134675321820545156> para unirte al clan en PS.\n\n"
            "🟢 **Xbox**\n"
            "Contacta a <@545943381784789042> para unirte al clan en Xbox.\n\n"
            "📱 **Resurgence (Móvil)**\n"
            "Contacta a <@526071764497989632> para unirte al clan en móvil.\n\n"
            "🩸 *Somos Sangre x Sangre en todas las plataformas. Elige la tuya y únete a la hermandad.*"
        )
        await ctx.send(mensaje)

async def setup(bot):
    await bot.add_cog(Mee6(bot))
