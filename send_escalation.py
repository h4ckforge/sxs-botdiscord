"""
Escalation Report Sender
Envía el reporte de escalation ahora (para pruebas)
"""
import requests
from datetime import datetime, timezone, timedelta

CLT = timezone(timedelta(hours=-3))
EVENT_JSON_URL = "https://hi-dep.github.io/division2/data/event/index.json"
REPORT_CHANNEL_ID = 1310237156895096922  # Test channel

# Role IDs
ROLE_DIVISION = 1477476638416441424
ROLE_ESCALADA = 1504140407297282108

def fetch_data():
    response = requests.get(EVENT_JSON_URL, timeout=30)
    response.raise_for_status()
    return response.json()

def get_today_escalation(data, today_str):
    escalations = data.get("Escalation", [])
    if not escalations:
        return None

    for week_data in reversed(escalations):
        week_str = week_data.get("week")
        if not week_str:
            continue

        target_loot_by_day = week_data.get("target_loot_by_day", [])
        for day_entry in target_loot_by_day:
            if day_entry.get("day") == today_str:
                return {
                    "week": week_str,
                    "missions": week_data.get("missions", []),
                    "target_loot": day_entry.get("target_loot", []),
                    "prototype_gear_cache": day_entry.get("prototype_gear_cache", ""),
                    "prototype_weapon_cache": day_entry.get("prototype_weapon_cache", ""),
                }
    return None

def build_message(data, today_str):
    missions = data.get("missions", [])
    target_loot = data.get("target_loot", [])
    gear_cache = data.get("prototype_gear_cache", "")
    weapon_cache = data.get("prototype_weapon_cache", "")

    mission_lines = []
    for i, (mission, loot) in enumerate(zip(missions, target_loot), 1):
        mission_lines.append(f"{i}.    {mission}  - {loot}")

    while len(target_loot) < len(missions):
        target_loot.append("—")

    requisition_lines = []
    if gear_cache:
        requisition_lines.append(f"1.    Prototype Gear Cache - {gear_cache.capitalize()}")
    if weapon_cache:
        requisition_lines.append(f"2.    Prototype Weapon Cache - {weapon_cache.capitalize()}")

    lines = [
        f"# Escalation Target Loot {today_str}",
        "",
        "### :round_pushpin:  Mission    Target Loot",
    ]
    lines.extend(mission_lines)
    lines.append("")
    lines.append("### :package: Escalation Requisition Vendor")
    lines.extend(requisition_lines)
    lines.append("")
    lines.append(f"<@&{ROLE_DIVISION}> <@&{ROLE_ESCALADA}>")

    return "\n".join(lines)

def send_message(token, channel_id, message):
    response = requests.post(
        f"https://discord.com/api/v10/channels/{channel_id}/messages",
        headers={'Authorization': f'Bot {token}', 'Content-Type': 'application/json'},
        json={'content': message}
    )
    return response.ok

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()

    today_str = datetime.now(CLT).strftime("%Y-%m-%d")
    print(f"Fetching escalation data for {today_str}...")

    data = fetch_data()
    escalation = get_today_escalation(data, today_str)

    if not escalation:
        print(f"No data found for {today_str}")
        exit(1)

    message = build_message(escalation, today_str)

    token = os.getenv('DISCORD_TOKEN')
    ok = send_message(token, REPORT_CHANNEL_ID, message)

    if ok:
        print(f"Report sent to channel {REPORT_CHANNEL_ID}!")
    else:
        print("Failed to send report")