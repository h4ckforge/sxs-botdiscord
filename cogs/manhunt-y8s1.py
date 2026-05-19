"""
Division 2 Y8S1 "Rise Up" Manhunt Scout Reporter
Envía Scout 9 (martes 26 mayo) y Climax (martes 2 junio) automáticamente.
"""

import json
import asyncio
from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta

CLT = timezone(timedelta(hours=-3))

REPORT_CHANNEL_ID = 1506313329528799243  # Thread Scout 8-9 y Climax
ROLES = [1477476638416441424, 1338158802901536901]

DATA_FILE = "data/manhunt-y8s1.json"


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


class ManhuntY8S1Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler.start()

    async def cog_unload(self):
        self.scheduler.cancel()

    @tasks.loop(hours=24)
    async def scheduler(self):
        await self.check_and_send()

    @scheduler.before_loop
    async def before_scheduler(self):
        await self.bot.wait_until_ready()
        now = datetime.now(CLT)
        target_hour, target_minute = 5, 30

        next_run = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)

        wait_seconds = (next_run - now).total_seconds()
        print(f"[Manhunt Y8S1] Próximo mensaje scheduled para {next_run} CLT ({wait_seconds:.0f}s)")
        await asyncio.sleep(wait_seconds)

    async def check_and_send(self):
        now = datetime.now(CLT)
        today = now.date()

        # Scout 9 → 26 mayo 2026
        scout9_date = datetime(2026, 5, 26, tzinfo=CLT).date()
        if today == scout9_date:
            await self.send_scout(9)
            return

        # Climax → 2 junio 2026
        climax_date = datetime(2026, 6, 2, tzinfo=CLT).date()
        if today == climax_date:
            await self.send_climax()
            return

        print(f"[Manhunt Y8S1] {today} — sin mensaje programado para hoy")

    async def send_scout(self, scout_num: int):
        try:
            data = load_data()
            scout_data = next((s for s in data["scouts"] if s["scout"] == scout_num), None)
            if not scout_data:
                print(f"[Manhunt Y8S1] Scout {scout_num} no encontrado")
                return

            today_str = datetime.now(CLT).strftime("%Y-%m-%d")
            message = self.build_scout_message(scout_data, today_str)
            channel = self.bot.get_channel(REPORT_CHANNEL_ID)
            if channel:
                await channel.send(message)
                print(f"[Manhunt Y8S1] Scout {scout_num} enviado")
            else:
                print(f"[Manhunt Y8S1] Canal {REPORT_CHANNEL_ID} no encontrado")
        except Exception as e:
            print(f"[Manhunt Y8S1] Error: {e}")

    async def send_climax(self):
        try:
            today_str = datetime.now(CLT).strftime("%Y-%m-%d")
            message = self.build_climax_message(today_str)
            channel = self.bot.get_channel(REPORT_CHANNEL_ID)
            if channel:
                await channel.send(message)
                print(f"[Manhunt Y8S1] Climax enviado")
            else:
                print(f"[Manhunt Y8S1] Canal {REPORT_CHANNEL_ID} no encontrado")
        except Exception as e:
            print(f"[Manhunt Y8S1] Error Climax: {e}")

    def build_scout_message(self, scout, today_str):
        hvt_label = f" **HVT {scout['hvt']}**" if "hvt" in scout else ""
        header = f"# Y8S1 \"Rise Up\" — Scout {scout['scout']}{hvt_label} - {today_str}"
        location_line = f"\n:map:  {scout['location']}\n"
        objective_lines = [f"• {obj}" for obj in scout.get("objectives", [])]
        role_mentions = " ".join(f"<@&{rid}>" for rid in ROLES)
        return "\n".join([header, location_line] + objective_lines + ["", role_mentions])

    def build_climax_message(self, today_str):
        header = f'# Y8S1 "Rise Up" — Climax - {today_str}'
        location_line = "\n:map:  The Pentagon\n"
        objective_lines = ['• Encontrar y derrotar a Jensen **"The Director" Sykes**']
        role_mentions = " ".join(f"<@&{rid}>" for rid in ROLES)
        return "\n".join([header, location_line] + objective_lines + ["", role_mentions])


async def setup(bot):
    await bot.add_cog(ManhuntY8S1Cog(bot))