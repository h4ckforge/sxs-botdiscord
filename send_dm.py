import os
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Format exactly as user specified
message = """# Escalation Target Loot 2026-05-13

### :round_pushpin:  Mission    Target Loot
1.    Pathway Park  - Badger Tuff
2.    Camp White Oak - Airaldi Holdings
3.    Grand Washington Hotel - 5.11 Tactical
4.    Jefferson Trade Center - Legatus S.p.A.
5.    Federal Emergency Bunker - Backpack

### :gem: Escalation Requisition Vendor
1.    Prototype Gear Cache - Mask
2.    Prototype Weapon Cache - Shotgun

<@&1477476638416441424> <@&1504140407297282108>"""

channel_id = 1310237156895096922
requests.post(f"https://discord.com/api/v10/channels/{channel_id}/messages",
    headers={'Authorization': f'Bot {TOKEN}', 'Content-Type': 'application/json'},
    json={'content': message}
)
print("Message sent!")