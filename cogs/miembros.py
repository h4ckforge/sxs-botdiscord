import discord
from discord.ext import commands
from utils import db

PLATAFORMAS_MAP = {
    'PC': 'pc',
    'PS': 'ps',
    'XBOX': 'xbox',
    'RESURGENCE': 'resurgence'
}

class Miembros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='registrar')
    @commands.has_permissions(administrator=True)
    async def registrar(self, ctx, usuario: discord.Member, plataforma: str, ign: str, clan: str):
        """Registra un miembro nuevo o actualiza uno existente en el clan.
        Uso: !registrar @usuario PC NombreEnJuego NombreClan"""

        plataforma_norm = plataforma.upper()
        if plataforma_norm not in PLATAFORMAS_MAP:
            await ctx.send(f"❌ Plataforma inválida. Opciones: {', '.join(PLATAFORMAS_MAP.keys())}")
            return

        campo_ign = f"ign_{PLATAFORMAS_MAP[plataforma_norm]}"
        campo_clan = f"clan_{PLATAFORMAS_MAP[plataforma_norm]}"

        existente = db.get("miembros", {"discord_user_id": str(usuario.id)})

        if existente:
            db.update(
                "miembros",
                {
                    campo_ign: ign,
                    campo_clan: clan,
                    "nombre": usuario.display_name,
                    "avatar": str(usuario.avatar) if usuario.avatar else None
                },
                {"discord_user_id": str(usuario.id)}
            )
            accion = "actualizado"
        else:
            db.insert("miembros", {
                "discord_user_id": str(usuario.id),
                "nombre": usuario.display_name,
                "avatar": str(usuario.avatar) if usuario.avatar else None,
                campo_ign: ign,
                campo_clan: clan
            })
            accion = "registrado"

        embed = discord.Embed(title="✅ Agente registrado", color=0xB22222)
        embed.add_field(name="Agente", value=usuario.mention, inline=True)
        embed.add_field(name="Plataforma", value=plataforma_norm, inline=True)
        embed.add_field(name="IGN", value=ign, inline=True)
        embed.add_field(name="Clan", value=clan, inline=True)
        embed.set_footer(text=f"Agente {accion} correctamente")
        await ctx.send(embed=embed)

    @commands.command(name='miembros')
    async def miembros(self, ctx, plataforma: str = None):
        """Lista miembros registrados por plataforma.
        Uso: !miembros [PC|PS|XBOX|RESURGENCE]"""

        if plataforma:
            plataforma_norm = plataforma.upper()
            if plataforma_norm not in PLATAFORMAS_MAP:
                await ctx.send(f"❌ Plataforma inválida. Opciones: {', '.join(PLATAFORMAS_MAP.keys())}")
                return

            sufijo = PLATAFORMAS_MAP[plataforma_norm]
            todos = db.get("miembros")
            registrados = [m for m in todos if m.get(f'ign_{sufijo}')]

            if not registrados:
                await ctx.send(f"❌ No hay miembros registrados en {plataforma_norm}.")
                return

            lineas = [f"· {m['nombre']} — IGN: `{m[f'ign_{sufijo}']}` | Clan: `{m[f'clan_{sufijo}'] or 'N/A'}`" for m in registrados]

            embed = discord.Embed(
                title=f"📋 Miembros {plataforma_norm} ({len(registrados)})",
                description="\n".join(lineas),
                color=0xB22222
            )
            await ctx.send(embed=embed)

        else:
            # Sin filtro: muestra resumen por plataforma
            todos = db.get("miembros")
            resumen = []
            for p, s in PLATAFORMAS_MAP.items():
                count = len([m for m in todos if m.get(f'ign_{s}')])
                resumen.append(f"{p}: {count} miembros")

            # Alertar miembros sin ninguna plataforma registrada
            sin_clan = [m for m in todos if not any(m.get(f'ign_{s}') for s in PLATAFORMAS_MAP.values())]

            embed = discord.Embed(title="📋 Resumen de miembros", color=0xB22222)
            embed.add_field(name="Por plataforma", value="\n".join(resumen), inline=False)
            if sin_clan:
                nombres = ", ".join([m['nombre'] for m in sin_clan])
                embed.add_field(name="⚠️ Sin clan registrado", value=nombres, inline=False)
            await ctx.send(embed=embed)

    @commands.command(name='perfil')
    async def perfil(self, ctx, usuario: discord.Member = None):
        """Muestra el perfil de un agente.
        Uso: !perfil [@usuario]"""

        usuario = usuario or ctx.author
        datos = db.get("miembros", {"discord_user_id": str(usuario.id)})

        if not datos:
            await ctx.send(f"❌ {usuario.display_name} no está registrado en el clan.")
            return

        m = datos[0]

        embed = discord.Embed(
            title=f"🪖 Agente {usuario.display_name}",
            color=0xB22222
        )

        if usuario.avatar:
            embed.set_thumbnail(url=usuario.avatar.url)

        # Plataformas registradas
        plataformas = []
        if m.get('ign_pc'):
            plataformas.append(f"🖥️ PC — IGN: `{m['ign_pc']}` | Clan: `{m['clan_pc'] or 'N/A'}`")
        if m.get('ign_ps'):
            plataformas.append(f"🎮 PS — IGN: `{m['ign_ps']}` | Clan: `{m['clan_ps'] or 'N/A'}`")
        if m.get('ign_xbox'):
            plataformas.append(f"🟢 Xbox — IGN: `{m['ign_xbox']}` | Clan: `{m['clan_xbox'] or 'N/A'}`")
        if m.get('ign_resurgence'):
            plataformas.append(f"📱 Resurgence — IGN: `{m['ign_resurgence']}` | Clan: `{m['clan_resurgence'] or 'N/A'}`")

        if plataformas:
            embed.add_field(name="Plataformas", value="\n".join(plataformas), inline=False)
        else:
            embed.add_field(name="Plataformas", value="Sin plataformas registradas", inline=False)

        embed.add_field(name="XP", value="— (disponible en temporada)", inline=True)
        embed.add_field(name="Shepherd", value="— (disponible próximamente)", inline=True)
        embed.set_footer(text=f"ID Discord: {usuario.id}")

        await ctx.send(embed=embed)

    @commands.command(name='baja-clan')
    @commands.has_permissions(administrator=True)
    async def baja_clan(self, ctx, usuario: discord.Member, plataforma: str):
        """Elimina el registro de un miembro en una plataforma específica.
        Uso: !baja-clan @usuario PC"""

        plataforma_norm = plataforma.upper()
        if plataforma_norm not in PLATAFORMAS_MAP:
            await ctx.send(f"❌ Plataforma inválida. Opciones: {', '.join(PLATAFORMAS_MAP.keys())}")
            return

        existente = db.get("miembros", {"discord_user_id": str(usuario.id)})
        if not existente:
            await ctx.send(f"❌ {usuario.display_name} no está registrado.")
            return

        sufijo = PLATAFORMAS_MAP[plataforma_norm]
        db.update(
            "miembros",
            {f"ign_{sufijo}": None, f"clan_{sufijo}": None},
            {"discord_user_id": str(usuario.id)}
        )

        embed = discord.Embed(title="🔴 Baja de clan registrada", color=0x555555)
        embed.add_field(name="Agente", value=usuario.mention, inline=True)
        embed.add_field(name="Plataforma", value=plataforma_norm, inline=True)
        embed.set_footer(text="IGN y clan eliminados para esta plataforma")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Miembros(bot))
