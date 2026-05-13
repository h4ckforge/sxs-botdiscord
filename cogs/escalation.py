"""
Division 2 Escalation Scraper
Fetches daily escalation target loot and requisition vendor from hi-dep.github.io
Sends report to configured Discord channel daily at 06:00 CLT (UTC-3)
"""

from discord.ext import commands, tasks
import requests
import asyncio
from datetime import datetime, timezone, timedelta

# Chile timezone (UTC-3)
CLT = timezone(timedelta(hours=-3))

# Channel to send reports
REPORT_CHANNEL_ID = 1501254781715484974  # Thread real

# Source data URL
EVENT_JSON_URL = "https://hi-dep.github.io/division2/data/event/index.json"


class Division2Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scraper.start()

    def cog_unload(self):
        self.scraper.cancel()

    @tasks.loop(hours=24)  # Daily at 06:30 CLT
    async def scraper(self):
        await self.send_escalation_report()

    @scraper.before_loop
    async def before_scraper(self):
        """Wait until 06:30 CLT before first run"""
        await self.bot.wait_until_ready()
        now = datetime.now(CLT)
        target_hour = 6
        target_minute = 30

        # Calculate next 06:30 CLT
        next_run = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)

        wait_seconds = (next_run - now).total_seconds()
        print(f"[Escalation] Next report scheduled for {next_run} CLT ({wait_seconds:.0f}s)")
        await asyncio.sleep(wait_seconds)

    async def send_escalation_report(self):
        """Fetch escalation data and send to Discord"""
        try:
            data = await self.fetch_event_data()
            if not data:
                return

            today_str = datetime.now(CLT).strftime("%Y-%m-%d")
            escalation_data = self.get_today_escalation(data, today_str)

            if not escalation_data:
                print(f"[Division2] No escalation data for {today_str}")
                return

            message = self.build_message(escalation_data, today_str)
            channel = self.bot.get_channel(REPORT_CHANNEL_ID)
            if channel:
                await channel.send(message)
                print(f"[Division2] Escalation report sent for {today_str}")
            else:
                print(f"[Division2] Channel {REPORT_CHANNEL_ID} not found")

        except Exception as e:
            print(f"[Division2] Error sending report: {e}")

    async def fetch_event_data(self):
        """Fetch event JSON from source"""
        try:
            response = requests.get(EVENT_JSON_URL, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[Division2] Failed to fetch data: {e}")
            return None

    def get_today_escalation(self, data, today_str):
        """Extract escalation data for a specific day"""
        escalations = data.get("Escalation", [])
        if not escalations:
            return None

        # Find the week containing today
        today_date = datetime.strptime(today_str, "%Y-%m-%d").date()

        for week_data in reversed(escalations):  # Most recent first
            week_str = week_data.get("week")
            if not week_str:
                continue

            week_date = datetime.strptime(week_str, "%Y-%m-%d").date()
            target_loot_by_day = week_data.get("target_loot_by_day", [])

            # Look for exact day match
            for day_entry in target_loot_by_day:
                if day_entry.get("day") == today_str:
                    return {
                        "week": week_str,
                        "missions": week_data.get("missions", []),
                        "target_loot": day_entry.get("target_loot", []),
                        "prototype_gear_cache": day_entry.get("prototype_gear_cache", ""),
                        "prototype_weapon_cache": day_entry.get("prototype_weapon_cache", ""),
                    }

            # If today is within this week's range but no exact match, use the week's data
            # Find the Sunday of this week (DD calculates the week starting Sunday)
            days_since_sunday = (today_date.weekday() + 1) % 7
            week_start = today_date - timedelta(days=days_since_sunday)
            if week_date == week_start and target_loot_by_day:
                # Use the first available day's data
                day_entry = target_loot_by_day[0]
                return {
                    "week": week_str,
                    "missions": week_data.get("missions", []),
                    "target_loot": day_entry.get("target_loot", []),
                    "prototype_gear_cache": day_entry.get("prototype_gear_cache", ""),
                    "prototype_weapon_cache": day_entry.get("prototype_weapon_cache", ""),
                }

        return None

    def build_message(self, data, today_str):
        """Build Discord message from escalation data"""
        missions = data.get("missions", [])
        target_loot = data.get("target_loot", [])
        gear_cache = data.get("prototype_gear_cache", "")
        weapon_cache = data.get("prototype_weapon_cache", "")

        # Format missions and target loot as numbered list
        mission_lines = []
        for i, (mission, loot) in enumerate(zip(missions, target_loot), 1):
            mission_lines.append(f"{i}.    {mission}  - {loot}")

        # Handle case where we have fewer loot items than missions
        while len(target_loot) < len(missions):
            target_loot.append("—")
        while len(missions) < len(target_loot):
            missions.append("—")

        # Requisition vendor section
        requisition_lines = []
        if gear_cache:
            requisition_lines.append(f"1.    Prototype Gear Cache - {gear_cache.capitalize()}")
        if weapon_cache:
            requisition_lines.append(f"2.    Prototype Weapon Cache - {weapon_cache.capitalize()}")

        # Build message
        lines = [
            f"# Escalation Target Loot {today_str}",
            "",
            "### :round_pushpin:  Mission    Target Loot",
        ]
        lines.extend(mission_lines)
        lines.append("")
        lines.append("###  :package:  Escalation Requisition Vendor")
        lines.extend(requisition_lines)
        lines.append("")
        lines.append("<@&1477476638416441424> <@&1504140407297282108>")

        return "\n".join(lines)


async def setup(bot):
    await bot.add_cog(Division2Cog(bot))