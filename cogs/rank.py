import discord
from discord.ext import commands
from discord.ext import tasks
from utils import db
from utils.xp_calc import calcular_nivel, xp_para_siguiente_nivel
from datetime import datetime

CANAL_RANKING_ID = 1493284581552685197
CANAL_RAIDS_ID = 1493286388731478308

class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ranking_message_id = None
        self.raids_message_id = None
        self.actualizar_ranking_loop.start()

    def cog_unload(self):
        self.actualizar_ranking_loop.cancel()

    def _get_temporada_activa(self):
        resultado = db.get("temporadas", {"activa": True})
        return resultado[0] if resultado else None

    def _construir_embed_raids(self):
        """Construye embed con las últimas 3 raids confirmadas."""
        todos_eventos = db.get("eventos")
        todos_miembros = db.get("miembros")
        miembros_map = {m["id"]: m["nombre"] for m in todos_miembros}
        todas_actividades = db.get("actividades")
        actividades_map = {a["id"]: a for a in todas_actividades}

        raids = [
            e for e in todos_eventos
            if e["estado"] == "confirmado" and
            actividades_map.get(e["actividad_id"], {}).get("is_raid", False)
        ]
        raids = sorted(raids, key=lambda e: e["fecha_evento"] or "", reverse=True)[:3]

        embed = discord.Embed(
            title="🏆 Historial de Raids",
            description=f"Sangre x Sangre — Últimas {len(raids)} raid{'s' if len(raids) != 1 else ''} realizadas",
            color=0xB22222
        )

        if not raids:
            embed.add_field(name="Sin raids", value="Aún no hay raids confirmadas.", inline=False)
        else:
            for i, raid in enumerate(raids, 1):
                actividad = actividades_map.get(raid["actividad_id"], {})
                creador = miembros_map.get(raid["creador_id"], "Desconocido")
                confirmador = miembros_map.get(raid["confirmado_por"], "—")
                fecha = datetime.fromisoformat(raid["fecha_evento"]).strftime("%d/%m/%Y • %H:%M") if raid["fecha_evento"] else "—"

                participantes = db.get("participantes_evento", {"evento_id": raid["id"], "es_reserva": False})
                nombres_p = "\n".join([f"• {miembros_map.get(p['miembro_id'], '?')}" for p in participantes])

                medalla = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "⚔️")

                valor = (
                    f"⚔️ **{actividad.get('nombre', '?')}**\n"
                    f"📅 {fecha}\n"
                    f"👤 Creada por: **{creador}**\n"
                    f"✨ XP Total: **{raid['xp_total_concedido']} XP**\n"
                    f"✅ Confirmada por: **{confirmador}**\n\n"
                    f"👥 **Participantes ({len(participantes)})**\n"
                    f"{nombres_p or 'N/A'}"
                )

                embed.add_field(
                    name=f"{medalla} RAID #{i}",
                    value=valor,
                    inline=False
                )

                if i < len(raids):
                    embed.add_field(name="―" * 30, value="", inline=False)

        embed.set_footer(text=f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        return embed

    async def actualizar_embed_raids(self):
        """Publica o actualiza el embed de historial de raids."""
        canal = self.bot.get_channel(CANAL_RAIDS_ID)
        if not canal:
            return

        embed = self._construir_embed_raids()

        try:
            if self.raids_message_id:
                mensaje = await canal.fetch_message(self.raids_message_id)
                await mensaje.edit(embed=embed)
            else:
                async for msg in canal.history(limit=10):
                    if msg.author == self.bot.user and msg.embeds:
                        self.raids_message_id = msg.id
                        await msg.edit(embed=embed)
                        return
                msg = await canal.send(embed=embed)
                self.raids_message_id = msg.id
        except discord.NotFound:
            msg = await canal.send(embed=embed)
            self.raids_message_id = msg.id
        except Exception as e:
            print(f"[RAIDS] Error actualizando embed: {e}")

    def _construir_embed_ranking(self, temporada, tipo="general"):
        todos = db.get("xp_temporada", {"temporada_id": temporada["id"]})
        todos_miembros = db.get("miembros")
        miembros_map = {m["id"]: m["nombre"] for m in todos_miembros}

        if tipo == "shepherd":
            shepherd_data = db.get("xp_shepherd")
            ordenados = sorted(shepherd_data, key=lambda r: r["xp_shepherd"], reverse=True)[:50]
            medallas = {1: "🥇", 2: "🥈", 3: "🥉"}
            lineas = []
            for i, r in enumerate(ordenados, 1):
                nombre = miembros_map.get(r["miembro_id"], "Desconocido")
                medalla = medallas.get(i, f"{i}.")
                lineas.append(f"{medalla} {nombre} • {r['xp_shepherd']} XP")
            titulo = f"🐺 Ranking Shepherd"
        else:
            campo_orden = "xp_eventos" if tipo == "eventos" else "xp_total"
            ordenados = sorted(todos, key=lambda r: r[campo_orden], reverse=True)[:50]
            medallas = {1: "🥇", 2: "🥈", 3: "🥉"}
            lineas = []
            for i, r in enumerate(ordenados, 1):
                nombre = miembros_map.get(r["miembro_id"], "Desconocido")
                medalla = medallas.get(i, f"{i}.")
                xp = r[campo_orden]
                lineas.append(f"{medalla} {nombre} • Nv{r['nivel']} • {xp} XP")
            titulo = f"🏆 Ranking — {temporada['nombre']}"

        if not lineas:
            lineas = ["Sin datos aún"]

        col1 = "\n".join(lineas[:25])
        col2 = "\n".join(lineas[25:]) if len(lineas) > 25 else None

        embed = discord.Embed(title=titulo, color=0xB22222)
        embed.add_field(name="📊 Posición 1-25", value=col1, inline=True)
        if col2:
            embed.add_field(name="📊 Posición 26-50", value=col2, inline=True)
        embed.set_footer(text=f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        return embed

    @tasks.loop(minutes=30)
    async def actualizar_ranking_loop(self):
        """Actualiza el embed de ranking automáticamente cada 30 minutos."""
        await self.bot.wait_until_ready()
        temporada = self._get_temporada_activa()
        if not temporada:
            return

        canal = self.bot.get_channel(CANAL_RANKING_ID)
        if not canal:
            return

        embed = self._construir_embed_ranking(temporada, "general")

        try:
            if self.ranking_message_id:
                mensaje = await canal.fetch_message(self.ranking_message_id)
                await mensaje.edit(embed=embed)
            else:
                # Buscar mensaje existente del bot en el canal
                async for msg in canal.history(limit=10):
                    if msg.author == self.bot.user and msg.embeds:
                        self.ranking_message_id = msg.id
                        await msg.edit(embed=embed)
                        return
                # Si no existe, crear uno nuevo
                msg = await canal.send(embed=embed)
                self.ranking_message_id = msg.id
        except discord.NotFound:
            msg = await canal.send(embed=embed)
            self.ranking_message_id = msg.id
        except Exception as e:
            print(f"[RANKING] Error actualizando embed: {e}")

    @commands.command(name='rank')
    async def rank(self, ctx, usuario: discord.Member = None):
        """Muestra el XP y posición de un agente en la temporada actual.
        Uso: !rank [@usuario]"""

        usuario = usuario or ctx.author
        temporada = self._get_temporada_activa()

        if not temporada:
            await ctx.send("❌ No hay ninguna temporada activa.")
            return

        miembro = db.get("miembros", {"discord_user_id": str(usuario.id)})
        if not miembro:
            await ctx.send(f"❌ {usuario.display_name} no está registrado en el clan.")
            return

        miembro_id = miembro[0]["id"]
        xp_data = db.get("xp_temporada", {
            "miembro_id": miembro_id,
            "temporada_id": temporada["id"]
        })

        if not xp_data:
            await ctx.send(f"❌ {usuario.display_name} no tiene XP en la temporada actual.")
            return

        x = xp_data[0]
        progreso = xp_para_siguiente_nivel(x["xp_total"])

        todos = db.get("xp_temporada", {"temporada_id": temporada["id"]})
        ordenados = sorted(todos, key=lambda r: r["xp_total"], reverse=True)
        posicion = next((i + 1 for i, r in enumerate(ordenados) if r["miembro_id"] == miembro_id), None)

        embed = discord.Embed(title=f"🏆 {usuario.display_name}", color=0xB22222)
        if usuario.avatar:
            embed.set_thumbnail(url=usuario.avatar.url)

        embed.add_field(name="Temporada", value=temporada["nombre"], inline=False)
        embed.add_field(name="Nivel", value=f"Nv{x['nivel']}", inline=True)
        embed.add_field(name="XP Total", value=str(x["xp_total"]), inline=True)
        embed.add_field(name="Posición", value=f"#{posicion}", inline=True)
        embed.add_field(name="XP Eventos", value=str(x["xp_eventos"]), inline=True)
        embed.add_field(name="Eventos participados", value=str(x["eventos_participados"]), inline=True)
        embed.add_field(name="Eventos creados", value=str(x["eventos_creados"]), inline=True)

        if progreso["nivel_siguiente"] is not None:
            embed.add_field(
                name="Próximo nivel",
                value=f"Nv{progreso['nivel_siguiente']} — faltan {progreso['xp_faltante']} XP",
                inline=False
            )
        else:
            embed.add_field(name="Nivel máximo", value="🎖️ Nivel máximo alcanzado", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='ranking')
    async def ranking(self, ctx, tipo: str = "general"):
        """Muestra el ranking de la temporada actual.
        Uso: !ranking [general|eventos|shepherd]"""

        tipo = tipo.lower()
        if tipo not in ["general", "eventos", "shepherd"]:
            await ctx.send("❌ Tipo inválido. Opciones: `general`, `eventos`, `shepherd`")
            return

        temporada = self._get_temporada_activa()
        if not temporada:
            await ctx.send("❌ No hay ninguna temporada activa.")
            return

        embed = self._construir_embed_ranking(temporada, tipo)
        await ctx.send(embed=embed)

    @commands.command(name='shepherd')
    async def shepherd(self, ctx, usuario: discord.Member = None):
        """Muestra el XP Shepherd acumulado de un agente.
        Uso: !shepherd [@usuario]"""

        usuario = usuario or ctx.author
        miembro = db.get("miembros", {"discord_user_id": str(usuario.id)})

        if not miembro:
            await ctx.send(f"❌ {usuario.display_name} no está registrado en el clan.")
            return

        miembro_id = miembro[0]["id"]
        shepherd = db.get("xp_shepherd", {"miembro_id": miembro_id})

        if not shepherd:
            await ctx.send(f"❌ {usuario.display_name} aún no tiene XP Shepherd.")
            return

        s = shepherd[0]
        embed = discord.Embed(title=f"🐺 Shepherd — {usuario.display_name}", color=0xB22222)
        if usuario.avatar:
            embed.set_thumbnail(url=usuario.avatar.url)

        embed.add_field(name="XP Shepherd", value=str(s["xp_shepherd"]), inline=True)
        embed.add_field(name="Raids participadas", value=str(s["raids_participadas"]), inline=True)
        embed.add_field(name="Raids creadas", value=str(s["raids_creadas"]), inline=True)
        embed.set_footer(text="El XP Shepherd nunca se resetea")
        await ctx.send(embed=embed)

    @commands.command(name='historial')
    async def historial(self, ctx, usuario: discord.Member = None):
        """Muestra los últimos eventos confirmados de un agente.
        Uso: !historial [@usuario]"""

        usuario = usuario or ctx.author
        miembro = db.get("miembros", {"discord_user_id": str(usuario.id)})

        if not miembro:
            await ctx.send(f"❌ {usuario.display_name} no está registrado en el clan.")
            return

        miembro_id = miembro[0]["id"]
        todas_participaciones = db.get("participantes_evento", {"miembro_id": miembro_id, "confirmado": True})

        if not todas_participaciones:
            await ctx.send(f"❌ {usuario.display_name} aún no tiene eventos confirmados.")
            return

        todos_eventos = db.get("eventos")
        eventos_map = {e["id"]: e for e in todos_eventos}
        todas_actividades = db.get("actividades")
        actividades_map = {a["id"]: a for a in todas_actividades}

        # Ordenar por evento más reciente
        participaciones = sorted(
            todas_participaciones,
            key=lambda p: eventos_map.get(p["evento_id"], {}).get("fecha_evento") or "",
            reverse=True
        )[:10]

        embed = discord.Embed(
            title=f"📜 Historial de {usuario.display_name}",
            color=0xB22222
        )
        if usuario.avatar:
            embed.set_thumbnail(url=usuario.avatar.url)

        for p in participaciones:
            evento = eventos_map.get(p["evento_id"])
            if not evento:
                continue
            actividad = actividades_map.get(evento["actividad_id"], {})
            fecha = datetime.fromisoformat(evento["fecha_evento"]).strftime("%d/%m/%Y") if evento["fecha_evento"] else "—"
            es_creador = evento["creador_id"] == miembro_id
            emoji = "⚔️" if actividad.get("is_raid") else "🎯"

            embed.add_field(
                name=f"{emoji} {actividad.get('nombre', '?')} — {fecha}",
                value=(
                    f"XP ganado: **{p['xp_ganado']} XP**"
                    + (" 👑 Creador" if es_creador else "")
                ),
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='info-xp')
    async def info_xp(self, ctx):
        """Explica cómo funciona el sistema de XP en Sangre x Sangre.
        Uso: !info-xp"""

        embed = discord.Embed(title="ℹ️ Sistema de XP — Sangre x Sangre", color=0xB22222)
        embed.add_field(
            name="🏆 XP de Temporada",
            value="Se gana participando y creando eventos.\nSe **resetea** al inicio de cada temporada.\nEl Top 1 al final de la temporada gana un premio.",
            inline=False
        )
        embed.add_field(
            name="🐺 XP Shepherd",
            value="Se gana igual que el XP de temporada.\n**Nunca se resetea.**\nDefine prioridad en la lista de espera para recibir exóticas de raids.",
            inline=False
        )
        embed.add_field(
            name="📊 Niveles",
            value="Nv0: 0 – 299 XP\nNv1: 300 – 699 XP\nNv2: 700 – 1,199 XP\nNv3: 1,200 – 1,799 XP\nNv4: 1,800+ XP",
            inline=False
        )
        embed.add_field(
            name="⚔️ XP por actividad",
            value="Raid: 60 XP + bonus creador\nIncursión / Legendaria Semanal: 20 XP\nMisión Legendaria: 15 XP\nOtras actividades: 5–10 XP",
            inline=False
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Rank(bot))
