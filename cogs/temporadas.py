import discord
from discord.ext import commands
from utils import db
from datetime import datetime

class Temporadas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='temporada-nueva')
    @commands.has_permissions(administrator=True)
    async def temporada_nueva(self, ctx, nombre: str, fecha_inicio: str, fecha_fin: str):
        """Crea una nueva temporada y resetea XP de temporada.
        Uso: !temporada-nueva "Nombre" DD/MM/YYYY DD/MM/YYYY"""

        try:
            inicio = datetime.strptime(fecha_inicio, "%d/%m/%Y")
            fin = datetime.strptime(fecha_fin, "%d/%m/%Y")
        except ValueError:
            await ctx.send("❌ Formato de fecha inválido. Usa DD/MM/YYYY. Ejemplo: `02/04/2026`")
            return

        if fin <= inicio:
            await ctx.send("❌ La fecha de fin debe ser posterior a la fecha de inicio.")
            return

        # Desactivar temporada actual
        db.update("temporadas", {"activa": False}, {"activa": True})

        # Crear nueva temporada
        resultado = db.insert("temporadas", {
            "nombre": nombre,
            "fecha_inicio": inicio.isoformat(),
            "fecha_fin": fin.isoformat(),
            "activa": True
        })

        if not resultado:
            await ctx.send("❌ Error al crear la temporada. Revisa la consola.")
            return

        nueva_temporada_id = resultado[0]["id"]

        # Crear filas xp_temporada para todos los miembros
        miembros = db.get("miembros")
        for m in miembros:
            db.insert("xp_temporada", {
                "miembro_id": m["id"],
                "temporada_id": nueva_temporada_id,
                "xp_eventos": 0,
                "xp_chat": 0,
                "xp_voz": 0,
                "xp_total": 0,
                "nivel": 1,
                "eventos_creados": 0,
                "eventos_participados": 0
            })

        embed = discord.Embed(
            title="✅ Nueva temporada creada",
            color=0xB22222
        )
        embed.add_field(name="Nombre", value=nombre, inline=False)
        embed.add_field(name="Inicio", value=fecha_inicio, inline=True)
        embed.add_field(name="Fin", value=fecha_fin, inline=True)
        embed.add_field(name="Agentes inicializados", value=str(len(miembros)), inline=True)
        embed.set_footer(text="XP Shepherd no fue modificado")
        await ctx.send(embed=embed)

    @commands.command(name='temporada-actual')
    async def temporada_actual(self, ctx):
        """Muestra información de la temporada activa.
        Uso: !temporada-actual"""

        resultado = db.get("temporadas", {"activa": True})

        if not resultado:
            await ctx.send("❌ No hay ninguna temporada activa.")
            return

        t = resultado[0]
        inicio = datetime.fromisoformat(t["fecha_inicio"]).strftime("%d/%m/%Y")
        fin = datetime.fromisoformat(t["fecha_fin"]).strftime("%d/%m/%Y")
        dias_restantes = (datetime.fromisoformat(t["fecha_fin"]) - datetime.now()).days

        embed = discord.Embed(
            title=f"🗓️ {t['nombre']}",
            color=0xB22222
        )
        embed.add_field(name="Inicio", value=inicio, inline=True)
        embed.add_field(name="Fin estimado", value=fin, inline=True)
        embed.add_field(name="Días restantes", value=str(dias_restantes), inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Temporadas(bot))
