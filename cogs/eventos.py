import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Select, Button
from utils import db
from utils.xp_calc import calcular_xp_evento, actualizar_xp_temporada, actualizar_xp_shepherd
from datetime import datetime, timedelta
import asyncio

CANAL_EVENTOS_ID = 1493278451598102598

# ============================================================
# MODAL — solo fecha y hora
# ============================================================
class FechaHoraModal(Modal, title="Fecha y hora del evento"):
    fecha = TextInput(
        label="Fecha (DD/MM/YYYY)",
        placeholder="Ej: 15/04/2026",
        max_length=10
    )
    hora = TextInput(
        label="Hora (HH:MM)",
        placeholder="Ej: 21:00",
        max_length=5
    )

    def __init__(self, actividad: dict, plataforma: str, miembro_id: int, creador: discord.Member):
        super().__init__()
        self.actividad = actividad
        self.plataforma = plataforma
        self.miembro_id = miembro_id
        self.creador = creador

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            fecha_evento = datetime.strptime(
                f"{self.fecha.value} {self.hora.value}", "%d/%m/%Y %H:%M"
            )
        except ValueError:
            await interaction.followup.send(
                "❌ Fecha u hora inválida. Usa formato DD/MM/YYYY y HH:MM.", ephemeral=True
            )
            return

        temporada = db.get("temporadas", {"activa": True})
        if not temporada:
            await interaction.followup.send("❌ No hay temporada activa.", ephemeral=True)
            return

        temporada_id = temporada[0]["id"]

        # Verificar cooldown 1 hora
        hace_una_hora = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        eventos_recientes = db.get("eventos", {"creador_id": self.miembro_id})
        eventos_recientes = [
            e for e in eventos_recientes
            if e["fecha_creacion"] and e["fecha_creacion"] > hace_una_hora
        ]
        if eventos_recientes:
            await interaction.followup.send(
                "❌ Solo puedes crear 1 evento por hora.", ephemeral=True
            )
            return

        # Crear evento en DB
        nuevo_evento = db.insert("eventos", {
            "actividad_id": self.actividad["id"],
            "creador_id": self.miembro_id,
            "temporada_id": temporada_id,
            "guild_id": str(interaction.guild_id),
            "channel_id": str(CANAL_EVENTOS_ID),
            "fecha_evento": fecha_evento.isoformat(),
            "estado": "abierto",
            "xp_total_concedido": 0
        })

        if not nuevo_evento:
            await interaction.followup.send("❌ Error al crear el evento.", ephemeral=True)
            return

        evento_id = nuevo_evento[0]["id"]

        # Agregar creador como primer participante
        db.insert("participantes_evento", {
            "evento_id": evento_id,
            "miembro_id": self.miembro_id,
            "es_reserva": False,
            "xp_ganado": 0,
            "confirmado": False
        })

        canal = interaction.guild.get_channel(CANAL_EVENTOS_ID)
        if not canal:
            await interaction.followup.send("❌ No encontré el canal de eventos.", ephemeral=True)
            return

        embed = construir_embed_evento(
            self.actividad, fecha_evento, self.creador,
            self.plataforma, [self.creador.display_name], []
        )

        view = EventoView(evento_id)
        mensaje = await canal.send(embed=embed, view=view)
        db.update("eventos", {"message_id": str(mensaje.id)}, {"id": evento_id})

        await interaction.followup.send("✅ Evento creado correctamente.", ephemeral=True)

        asyncio.create_task(
            auto_cancelar(interaction.client, evento_id, mensaje, self.actividad, fecha_evento)
        )


# ============================================================
# STEP 3 — Selector de plataforma
# ============================================================
class PlataformaSelect(View):
    def __init__(self, actividad: dict, miembro_id: int, creador: discord.Member):
        super().__init__(timeout=60)
        self.actividad = actividad
        self.miembro_id = miembro_id
        self.creador = creador

        select = Select(
            placeholder="Selecciona tu plataforma...",
            options=[
                discord.SelectOption(label="PC", emoji="🖥️"),
                discord.SelectOption(label="PS", emoji="🎮"),
                discord.SelectOption(label="Xbox", emoji="🟢"),
                discord.SelectOption(label="Resurgence", emoji="📱"),
            ]
        )
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        plataforma = interaction.data["values"][0]
        modal = FechaHoraModal(self.actividad, plataforma, self.miembro_id, self.creador)
        await interaction.response.send_modal(modal)


# ============================================================
# STEP 2 — Selector de actividad
# ============================================================
class ActividadSelect(View):
    def __init__(self, juego: str, miembro_id: int, creador: discord.Member):
        super().__init__(timeout=60)
        self.juego = juego
        self.miembro_id = miembro_id
        self.creador = creador

        actividades = db.get("actividades")
        actividades_juego = [a for a in actividades if a["juego"] == juego]

        opciones = []
        for a in actividades_juego[:25]:  # Discord max 25 opciones
            emoji = "⚔️" if a["is_raid"] else "🎯"
            opciones.append(discord.SelectOption(
                label=a["nombre"],
                value=str(a["id"]),
                emoji=emoji,
                description=f"{a['xp_base']} XP base"
            ))

        select = Select(placeholder="Selecciona una actividad...", options=opciones)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        actividad_id = int(interaction.data["values"][0])
        actividades = db.get("actividades")
        actividad = next((a for a in actividades if a["id"] == actividad_id), None)

        if not actividad:
            await interaction.response.send_message("❌ Actividad no encontrada.", ephemeral=True)
            return

        view = PlataformaSelect(actividad, self.miembro_id, self.creador)
        await interaction.response.edit_message(
            content=f"✅ **{actividad['nombre']}** seleccionada. Ahora elige tu plataforma:",
            view=view
        )


# ============================================================
# STEP 1 — Selector de juego
# ============================================================
class JuegoSelect(View):
    def __init__(self, miembro_id: int, creador: discord.Member):
        super().__init__(timeout=60)
        self.miembro_id = miembro_id
        self.creador = creador

        actividades = db.get("actividades")
        juegos = list(set(a["juego"] for a in actividades))

        opciones = [discord.SelectOption(label=j, value=j) for j in juegos]
        select = Select(placeholder="Selecciona el juego...", options=opciones)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        juego = interaction.data["values"][0]
        view = ActividadSelect(juego, self.miembro_id, self.creador)
        await interaction.response.edit_message(
            content=f"✅ **{juego}** seleccionado. Ahora elige la actividad:",
            view=view
        )


# ============================================================
# EMBED del evento
# ============================================================
def construir_embed_evento(actividad, fecha_evento, creador, plataforma, participantes, reservas):
    es_raid = actividad.get("is_raid", False)
    color = 0xB22222 if es_raid else 0x2F3136
    titulo = f"{'⚔️ RAID' if es_raid else '🎯 EVENTO'} — {actividad['nombre']}"

    embed = discord.Embed(title=titulo, color=color)
    embed.add_field(name="Juego", value=actividad["juego"], inline=True)
    embed.add_field(name="Plataforma", value=plataforma, inline=True)
    embed.add_field(name="Fecha", value=fecha_evento.strftime("%d/%m/%Y %H:%M"), inline=True)
    embed.add_field(name="Creado por", value=creador.display_name if creador else "—", inline=True)
    embed.add_field(name="XP base", value=f"{actividad['xp_base']} XP", inline=True)
    embed.add_field(name="Cupo", value=f"{len(participantes)}/{actividad['max_participantes']}", inline=True)

    participantes_str = "\n".join(f"• {p}" for p in participantes) if participantes else "Ninguno aún"
    embed.add_field(name=f"Participantes ({len(participantes)})", value=participantes_str, inline=False)

    if reservas:
        reservas_str = "\n".join(f"• {r}" for r in reservas)
        embed.add_field(name=f"Reservas ({len(reservas)})", value=reservas_str, inline=False)

    embed.set_footer(text=f"Estado: Abierto")
    return embed


# ============================================================
# AUTO-CANCELACIÓN
# ============================================================
async def auto_cancelar(bot, evento_id, mensaje, actividad, fecha_evento):
    espera = (fecha_evento - datetime.utcnow()).total_seconds() + 900
    if espera > 0:
        await asyncio.sleep(espera)

    evento = db.get("eventos", {"id": evento_id})
    if not evento or evento[0]["estado"] != "abierto":
        return

    participantes = db.get("participantes_evento", {"evento_id": evento_id, "es_reserva": False})
    if len(participantes) < actividad.get("min_participantes", 1):
        db.update("eventos", {"estado": "cancelado"}, {"id": evento_id})
        try:
            embed = mensaje.embeds[0]
            embed.color = 0x555555
            embed.set_footer(text="❌ Evento cancelado — participantes insuficientes")
            await mensaje.edit(embed=embed, view=None)
        except Exception:
            pass


# ============================================================
# BOTONES del evento
# ============================================================
class EventoView(View):
    def __init__(self, evento_id: int):
        super().__init__(timeout=None)
        self.evento_id = evento_id

    @discord.ui.button(label="Participar", style=discord.ButtonStyle.success, emoji="✅", custom_id="evento_participar")
    async def participar(self, interaction: discord.Interaction, button: Button):
        evento_id = await get_evento_id_from_message(interaction)
        if evento_id:
            await handle_participar(interaction, evento_id)

    @discord.ui.button(label="Cancelar Participación", style=discord.ButtonStyle.secondary, emoji="❌", custom_id="evento_cancelar_participacion")
    async def cancelar_participacion(self, interaction: discord.Interaction, button: Button):
        evento_id = await get_evento_id_from_message(interaction)
        if evento_id:
            await handle_cancelar_participacion(interaction, evento_id)

    @discord.ui.button(label="Confirmar Evento", style=discord.ButtonStyle.primary, emoji="🏆", custom_id="evento_confirmar")
    async def confirmar_evento(self, interaction: discord.Interaction, button: Button):
        evento_id = await get_evento_id_from_message(interaction)
        if evento_id:
            await handle_confirmar_evento(interaction, evento_id)

    @discord.ui.button(label="Cancelar Evento", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="evento_cancelar")
    async def cancelar_evento(self, interaction: discord.Interaction, button: Button):
        evento_id = await get_evento_id_from_message(interaction)
        if evento_id:
            await handle_cancelar_evento(interaction, evento_id)


class EventoViewPersistente(View):
    """View persistente para registrar en on_ready."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Participar", style=discord.ButtonStyle.success, emoji="✅", custom_id="evento_participar")
    async def participar(self, interaction: discord.Interaction, button: Button):
        evento_id = await get_evento_id_from_message(interaction)
        if evento_id:
            await handle_participar(interaction, evento_id)

    @discord.ui.button(label="Cancelar Participación", style=discord.ButtonStyle.secondary, emoji="❌", custom_id="evento_cancelar_participacion")
    async def cancelar_participacion(self, interaction: discord.Interaction, button: Button):
        evento_id = await get_evento_id_from_message(interaction)
        if evento_id:
            await handle_cancelar_participacion(interaction, evento_id)

    @discord.ui.button(label="Confirmar Evento", style=discord.ButtonStyle.primary, emoji="🏆", custom_id="evento_confirmar")
    async def confirmar_evento(self, interaction: discord.Interaction, button: Button):
        evento_id = await get_evento_id_from_message(interaction)
        if evento_id:
            await handle_confirmar_evento(interaction, evento_id)

    @discord.ui.button(label="Cancelar Evento", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="evento_cancelar")
    async def cancelar_evento(self, interaction: discord.Interaction, button: Button):
        evento_id = await get_evento_id_from_message(interaction)
        if evento_id:
            await handle_cancelar_evento(interaction, evento_id)


async def get_evento_id_from_message(interaction: discord.Interaction):
    """Busca el evento_id en la DB usando el message_id del mensaje."""
    try:
        message_id = str(interaction.message.id)
        eventos = db.get("eventos")
        evento = next((e for e in eventos if e["message_id"] == message_id), None)
        if not evento:
            await interaction.response.send_message("❌ No se encontró el evento.", ephemeral=True)
            return None
        return evento["id"]
    except Exception as e:
        print(f"[EVENTOS] Error buscando evento: {e}")
        return None


async def handle_participar(interaction: discord.Interaction, evento_id: int):
    await interaction.response.defer(ephemeral=True)

    evento = db.get("eventos", {"id": evento_id})
    if not evento or evento[0]["estado"] != "abierto":
        await interaction.followup.send("❌ Este evento ya no está disponible.", ephemeral=True)
        return

    miembro = db.get("miembros", {"discord_user_id": str(interaction.user.id)})
    if not miembro:
        await interaction.followup.send("❌ No estás registrado en el clan.", ephemeral=True)
        return

    miembro_id = miembro[0]["id"]
    actividad = db.get("actividades", {"id": evento[0]["actividad_id"]})[0]
    participantes = db.get("participantes_evento", {"evento_id": evento_id, "es_reserva": False})
    reservas = db.get("participantes_evento", {"evento_id": evento_id, "es_reserva": True})

    ya_participa = any(p["miembro_id"] == miembro_id for p in participantes + reservas)
    if ya_participa:
        await interaction.followup.send("❌ Ya estás inscrito en este evento.", ephemeral=True)
        return

    if len(participantes) < actividad["max_participantes"]:
        db.insert("participantes_evento", {
            "evento_id": evento_id, "miembro_id": miembro_id,
            "es_reserva": False, "xp_ganado": 0, "confirmado": False
        })
        await interaction.followup.send("✅ Te has unido al evento.", ephemeral=True)
    elif len(reservas) < actividad["max_reservas"]:
        db.insert("participantes_evento", {
            "evento_id": evento_id, "miembro_id": miembro_id,
            "es_reserva": True, "xp_ganado": 0, "confirmado": False
        })
        await interaction.followup.send(f"⏳ Estás en reserva (posición {len(reservas) + 1}).", ephemeral=True)
    else:
        await interaction.followup.send("❌ El evento está lleno.", ephemeral=True)
        return

    await actualizar_embed_evento(interaction, evento_id)


async def handle_cancelar_participacion(interaction: discord.Interaction, evento_id: int):
    await interaction.response.defer(ephemeral=True)

    miembro = db.get("miembros", {"discord_user_id": str(interaction.user.id)})
    if not miembro:
        await interaction.followup.send("❌ No estás registrado.", ephemeral=True)
        return

    miembro_id = miembro[0]["id"]
    participacion = db.get("participantes_evento", {"evento_id": evento_id, "miembro_id": miembro_id})

    if not participacion:
        await interaction.followup.send("❌ No estás inscrito en este evento.", ephemeral=True)
        return

    era_participante = not participacion[0]["es_reserva"]
    db.delete("participantes_evento", {"evento_id": evento_id, "miembro_id": miembro_id})

    if era_participante:
        reservas = db.get("participantes_evento", {"evento_id": evento_id, "es_reserva": True})
        if reservas:
            db.update("participantes_evento", {"es_reserva": False}, {"id": reservas[0]["id"]})

    await interaction.followup.send("✅ Has cancelado tu participación.", ephemeral=True)
    await actualizar_embed_evento(interaction, evento_id)


async def handle_confirmar_evento(interaction: discord.Interaction, evento_id: int):
    await interaction.response.defer(ephemeral=True)

    evento = db.get("eventos", {"id": evento_id})[0]
    miembro = db.get("miembros", {"discord_user_id": str(interaction.user.id)})

    if not miembro:
        await interaction.followup.send("❌ No estás registrado.", ephemeral=True)
        return

    miembro_id = miembro[0]["id"]
    if evento["creador_id"] != miembro_id and not miembro[0].get("is_admin", False):
        await interaction.followup.send("❌ Solo el creador o un admin puede confirmar.", ephemeral=True)
        return

    if evento["estado"] != "abierto":
        await interaction.followup.send("❌ Este evento ya fue procesado.", ephemeral=True)
        return

    actividad = db.get("actividades", {"id": evento["actividad_id"]})[0]
    participantes = db.get("participantes_evento", {"evento_id": evento_id, "es_reserva": False})

    xp_total = 0
    for p in participantes:
        es_creador_p = p["miembro_id"] == evento["creador_id"]
        xp = calcular_xp_evento(actividad, es_creador_p)
        db.update("participantes_evento", {"xp_ganado": xp, "confirmado": True}, {"id": p["id"]})
        actualizar_xp_temporada(p["miembro_id"], evento["temporada_id"], xp, es_creador_p)
        actualizar_xp_shepherd(p["miembro_id"], xp, actividad["is_raid"])
        xp_total += xp

    db.update("eventos", {
        "estado": "confirmado",
        "xp_total_concedido": xp_total,
        "confirmado_por": miembro_id
    }, {"id": evento_id})

    await interaction.followup.send(f"✅ Evento confirmado. {xp_total} XP distribuidos.", ephemeral=True)
    await actualizar_embed_evento(interaction, evento_id, confirmado=True, xp_total=xp_total)

    # Si es raid, actualizar embed de historial de raids
    if actividad["is_raid"]:
        try:
            rank_cog = interaction.client.cogs.get("Rank")
            if rank_cog:
                await rank_cog.actualizar_embed_raids()
        except Exception as e:
            print(f"[RAIDS] Error actualizando historial: {e}")


async def handle_cancelar_evento(interaction: discord.Interaction, evento_id: int):
    await interaction.response.defer(ephemeral=True)

    evento = db.get("eventos", {"id": evento_id})[0]
    miembro = db.get("miembros", {"discord_user_id": str(interaction.user.id)})

    if not miembro:
        await interaction.followup.send("❌ No estás registrado.", ephemeral=True)
        return

    miembro_id = miembro[0]["id"]
    if evento["creador_id"] != miembro_id and not miembro[0].get("is_admin", False):
        await interaction.followup.send("❌ Solo el creador o un admin puede cancelar.", ephemeral=True)
        return

    db.update("eventos", {"estado": "cancelado"}, {"id": evento_id})
    await interaction.followup.send("✅ Evento cancelado.", ephemeral=True)
    await actualizar_embed_evento(interaction, evento_id, cancelado=True)


async def actualizar_embed_evento(interaction, evento_id, confirmado=False, cancelado=False, xp_total=0):
    try:
        evento = db.get("eventos", {"id": evento_id})[0]
        actividad = db.get("actividades", {"id": evento["actividad_id"]})[0]
        participantes = db.get("participantes_evento", {"evento_id": evento_id, "es_reserva": False})
        reservas = db.get("participantes_evento", {"evento_id": evento_id, "es_reserva": True})

        todos_miembros = db.get("miembros")
        miembros_map = {m["id"]: m["nombre"] for m in todos_miembros}

        nombres_p = [miembros_map.get(p["miembro_id"], "?") for p in participantes]
        nombres_r = [miembros_map.get(r["miembro_id"], "?") for r in reservas]

        canal = interaction.guild.get_channel(CANAL_EVENTOS_ID)
        mensaje = await canal.fetch_message(int(evento["message_id"]))

        creador_data = db.get("miembros", {"id": evento["creador_id"]})[0]
        creador_discord = interaction.guild.get_member(int(creador_data["discord_user_id"]))
        fecha_evento = datetime.fromisoformat(evento["fecha_evento"])

        embed = construir_embed_evento(actividad, fecha_evento, creador_discord or interaction.user,
                                       "—", nombres_p, nombres_r)

        if confirmado:
            embed.color = 0x00AA00
            embed.set_footer(text=f"✅ Confirmado | XP distribuido: {xp_total}")
            await mensaje.edit(embed=embed, view=None)
        elif cancelado:
            embed.color = 0x555555
            embed.set_footer(text="❌ Evento cancelado")
            await mensaje.edit(embed=embed, view=None)
        else:
            await mensaje.edit(embed=embed)
    except Exception as e:
        print(f"[EVENTOS] Error actualizando embed: {e}")


# ============================================================
# COG
# ============================================================
class Eventos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='evento')
    async def evento(self, ctx):
        """Crea un nuevo evento con selector interactivo.
        Uso: !evento"""

        miembro = db.get("miembros", {"discord_user_id": str(ctx.author.id)})
        if not miembro:
            await ctx.send("❌ No estás registrado en el clan. Pide a un admin que te registre con `!registrar`.")
            return

        miembro_id = miembro[0]["id"]
        view = JuegoSelect(miembro_id, ctx.author)
        await ctx.send("🎮 Selecciona el juego para tu evento:", view=view)


async def setup(bot):
    await bot.add_cog(Eventos(bot))
