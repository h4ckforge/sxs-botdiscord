import discord
from discord.ext import commands
from discord.ui import View, Select
from utils import db
from datetime import datetime

ACTIVIDADES_CON_LISTA = ["Raid Horas Oscuras", "Raid Caballo de Hierro", "Incursión"]

class ListaEsperaSelect(View):
    def __init__(self, miembro_id: int, solo_ver: bool = False):
        super().__init__(timeout=60)
        self.miembro_id = miembro_id
        self.solo_ver = solo_ver

        actividades = db.get("actividades")
        opciones = [
            discord.SelectOption(
                label=a["nombre"],
                value=str(a["id"]),
                emoji="⚔️" if a["is_raid"] else "🎯",
                description=a["juego"]
            )
            for a in actividades
            if a["nombre"] in ACTIVIDADES_CON_LISTA
        ]

        if not opciones:
            opciones = [discord.SelectOption(label="Sin actividades disponibles", value="0")]

        select = Select(placeholder="Selecciona una actividad...", options=opciones)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        actividad_id = int(interaction.data["values"][0])
        if actividad_id == 0:
            await interaction.response.send_message("❌ No hay actividades disponibles.", ephemeral=True)
            return

        if self.solo_ver:
            await mostrar_lista(interaction, actividad_id)
        else:
            await inscribir_o_consultar(interaction, actividad_id, self.miembro_id)


async def inscribir_o_consultar(interaction: discord.Interaction, actividad_id: int, miembro_id: int):
    await interaction.response.defer(ephemeral=True)

    actividad = db.get("actividades", {"id": actividad_id})
    if not actividad:
        await interaction.followup.send("❌ Actividad no encontrada.", ephemeral=True)
        return
    actividad = actividad[0]

    # Verificar si ya está inscrito
    inscripcion = db.get("lista_espera", {
        "miembro_id": miembro_id,
        "actividad_id": actividad_id,
        "recibio_item": False
    })

    if inscripcion:
        posicion = inscripcion[0]["posicion"]
        await interaction.followup.send(
            f"ℹ️ Ya estás inscrito en la lista de **{actividad['nombre']}**.\n"
            f"📊 Tu posición actual: **#{posicion}**",
            ephemeral=True
        )
        return

    # Calcular posición (al final de la cola)
    cola = db.get("lista_espera", {"actividad_id": actividad_id, "recibio_item": False})
    nueva_posicion = len(cola) + 1

    db.insert("lista_espera", {
        "miembro_id": miembro_id,
        "actividad_id": actividad_id,
        "posicion": nueva_posicion,
        "recibio_item": False
    })

    await interaction.followup.send(
        f"✅ Te has inscrito en la lista de espera de **{actividad['nombre']}**.\n"
        f"📊 Tu posición: **#{nueva_posicion}**",
        ephemeral=True
    )


async def mostrar_lista(interaction: discord.Interaction, actividad_id: int):
    await interaction.response.defer(ephemeral=True)

    actividad = db.get("actividades", {"id": actividad_id})
    if not actividad:
        await interaction.followup.send("❌ Actividad no encontrada.", ephemeral=True)
        return
    actividad = actividad[0]

    cola = db.get("lista_espera", {"actividad_id": actividad_id, "recibio_item": False})
    cola = sorted(cola, key=lambda r: r["posicion"])

    if not cola:
        await interaction.followup.send(
            f"📋 La lista de espera de **{actividad['nombre']}** está vacía.",
            ephemeral=True
        )
        return

    todos_miembros = db.get("miembros")
    miembros_map = {m["id"]: m["nombre"] for m in todos_miembros}

    lineas = []
    for r in cola:
        nombre = miembros_map.get(r["miembro_id"], "Desconocido")
        fecha = datetime.fromisoformat(r["fecha_inscripcion"]).strftime("%d/%m/%Y") if r["fecha_inscripcion"] else "—"
        lineas.append(f"**#{r['posicion']}** {nombre} — inscrito el {fecha}")

    embed = discord.Embed(
        title=f"📋 Lista de espera — {actividad['nombre']}",
        description="\n".join(lineas),
        color=0xB22222
    )
    embed.set_footer(text=f"Total en cola: {len(cola)}")
    await interaction.followup.send(embed=embed, ephemeral=True)


class ListaEspera(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lista-espera')
    async def lista_espera(self, ctx):
        """Inscríbete en la lista de espera para exóticas de raids e incursiones.
        Uso: !lista-espera"""

        miembro = db.get("miembros", {"discord_user_id": str(ctx.author.id)})
        if not miembro:
            await ctx.send("❌ No estás registrado en el clan. Pide a un admin que te registre con `!registrar`.")
            return

        miembro_id = miembro[0]["id"]
        view = ListaEsperaSelect(miembro_id, solo_ver=False)
        await ctx.send("⚔️ Selecciona la actividad para inscribirte en la lista de espera:", view=view)

    @commands.command(name='ver-lista')
    @commands.has_permissions(administrator=True)
    async def ver_lista(self, ctx):
        """Muestra la lista de espera completa de una actividad (admin).
        Uso: !ver-lista"""

        view = ListaEsperaSelect(0, solo_ver=True)
        await ctx.send("📋 Selecciona la actividad para ver la lista:", view=view)

    @commands.command(name='salir-lista')
    async def salir_lista(self, ctx):
        """Sal de la lista de espera de una actividad.
        Uso: !salir-lista"""

        miembro = db.get("miembros", {"discord_user_id": str(ctx.author.id)})
        if not miembro:
            await ctx.send("❌ No estás registrado en el clan.")
            return

        miembro_id = miembro[0]["id"]

        actividades = db.get("actividades")
        inscripciones = db.get("lista_espera", {"miembro_id": miembro_id, "recibio_item": False})

        if not inscripciones:
            await ctx.send("❌ No estás inscrito en ninguna lista de espera.")
            return

        actividades_map = {a["id"]: a["nombre"] for a in actividades}
        opciones = [
            discord.SelectOption(
                label=actividades_map.get(i["actividad_id"], "?"),
                value=str(i["actividad_id"])
            )
            for i in inscripciones
        ]

        view = SalirListaView(miembro_id, opciones)
        await ctx.send("📋 ¿De qué lista quieres salir?", view=view)


class SalirListaView(View):
    def __init__(self, miembro_id: int, opciones: list):
        super().__init__(timeout=60)
        self.miembro_id = miembro_id

        select = Select(placeholder="Selecciona una actividad...", options=opciones)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        actividad_id = int(interaction.data["values"][0])

        db.delete("lista_espera", {
            "miembro_id": self.miembro_id,
            "actividad_id": actividad_id
        })

        # Reordenar posiciones
        cola = db.get("lista_espera", {"actividad_id": actividad_id, "recibio_item": False})
        cola = sorted(cola, key=lambda r: r["posicion"])
        for i, r in enumerate(cola, 1):
            db.update("lista_espera", {"posicion": i}, {"id": r["id"]})

        actividad = db.get("actividades", {"id": actividad_id})
        nombre = actividad[0]["nombre"] if actividad else "?"
        await interaction.followup.send(f"✅ Has salido de la lista de espera de **{nombre}**.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(ListaEspera(bot))
