import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from components.supabase import supabase
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo

def height_to_cm(height_str):
    if not height_str or "-" not in height_str:
        return None
    parts = height_str.split("-")
    try:
        feet = int(parts[0])
        inches = int(parts[1])
        return int(round(feet * 30.48 + inches * 2.54))
    except (ValueError, IndexError):
        return None

def lbs_to_kg(lbs):
    try:
        return int(round(int(lbs) * 0.453592))
    except (ValueError, TypeError):
        return None

active_players = players.get_active_players()
print(f"Found {len(active_players)} active players")

player_records = []

for i, p in enumerate(active_players):
    pid = p["id"]

    try:
        info = commonplayerinfo.CommonPlayerInfo(player_id=pid)
        data = info.get_dict()
    except Exception as e:
        print(f"Failed for {p['full_name']} (ID: {pid}): {e}")
        continue

    common_info = data["resultSets"][0]
    headers = common_info["headers"]
    row = common_info["rowSet"][0] if common_info["rowSet"] else []

    row_dict = dict(zip(headers, row))

    first_name = row_dict.get("FIRST_NAME", "")
    last_name = row_dict.get("LAST_NAME", "")
    full_name = row_dict.get("DISPLAY_FIRST_LAST", "")
    position = row_dict.get("POSITION", "")
    country = row_dict.get("COUNTRY", "")
    height = row_dict.get("HEIGHT", "")
    weight = row_dict.get("WEIGHT", "")
    roster_status = row_dict.get("ROSTERSTATUS", "")
    team_abbrev = row_dict.get("TEAM_ABBREVIATION", "")

    height_cm = height_to_cm(height)
    weight_kg = lbs_to_kg(weight)
    is_active = roster_status.lower() == "active"

    team_id = None
    if team_abbrev:
        team_res = supabase.table("teams") \
            .select("id") \
            .eq("abbreviation", team_abbrev) \
            .eq("league", "NBA") \
            .single() \
            .execute()
        team_id = team_res.data["id"] if team_res.data else None

    headshot_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{pid}.png"

    player_records.append({
        "league": "NBA",
        "team_id": team_id,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "position": position,
        "nationality": country,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "active": is_active,
        "headshot_url": headshot_url,
    })

    if (i + 1) % 50 == 0:
        print(f"Processed {i + 1}/{len(active_players)} players...")
        time.sleep(1)

    time.sleep(0.2)

print(f"Upserting {len(player_records)} players...")
response = supabase.table("players").upsert(player_records).execute()

if response.data:
    print("Inserted:", len(response.data))
else:
    print("Insert failed:", response)
