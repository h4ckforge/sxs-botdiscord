import discord
from discord.ext import commands

CATEGORIAS = {
    "⚔️ Eventos": ["evento", "lista-espera", "salir-lista"],
    "🏆 Rank & Perfil": ["rank", "ranking", "shepherd", "perfil", "historial", "info-xp"],
    "ℹ️ Información": ["ayuda", "plataformas", "raid", "primera-raid"],
    "🔐 Staff": ["registrar", "baja-agente", "baja-clan", "ver-lista", "temporada-nueva", "temporada-actual", "permisos", "reload"],
}

STAFF_CMDS = {"registrar", "baja-agente", "baja-clan", "ver-lista", "temporada-nueva", "temporada-actual", "permisos", "reload"}

class Ayuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ayuda')
    async def ayuda(self, ctx):
        """Muestra la lista de comandos disponibles.
        Uso: !ayuda"""

        es_admin = ctx.author.guild_permissions.administrator

        comandos_map = {cmd.name: cmd for cmd in self.bot.commands}

        embed = discord.Embed(
            title="📋 Comandos — Sangre x Sangre",
            color=0xB22222
        )

        for categoria, nombres in CATEGORIAS.items():
            if categoria == "🔐 Staff" and not es_admin:
                continue

            lineas = []
            for nombre in sorted(nombres):
                cmd = comandos_map.get(nombre)
                if not cmd:
                    continue
                doc = (cmd.help or "").strip().split("\n")
                descripcion = doc[0]
                uso = next((l.strip() for l in doc if l.strip().startswith("Uso:")), None)
                linea = f"`!{nombre}` — {descripcion}"
                if uso:
                    linea += f"\n┗ `{uso}`"
                lineas.append(linea)

            if lineas:
                embed.add_field(
                    name=f"\u200b",
                    value=f"**{categoria}**",
                    inline=False
                )
                embed.add_field(
                    name="​",
                    value="\n".join(lineas),
                    inline=False
                )

        embed.set_footer(text="Sangre x Sangre • The Division 2")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ayuda(bot))
