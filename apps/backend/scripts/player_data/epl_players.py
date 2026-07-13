import os
import sys
import time
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from dotenv import load_dotenv, find_dotenv
from components.supabase import supabase
from eplda import EPLAPI

load_dotenv(find_dotenv())

epl = EPLAPI()

PULSE_HEADERS = {
    "origin": "https://www.premierleague.com",
    "referer": "https://www.premierleague.com/",
}

POSITION_MAP = {"G": "Goalkeeper", "D": "Defender", "M": "Midfielder", "F": "Forward"}

CLUB_ABBR_MAP = {
    "Arsenal": "ARS",
    "Aston Villa": "AVL",
    "Bournemouth": "BOU",
    "Brentford": "BRE",
    "Brighton & Hove Albion": "BHA",
    "Chelsea": "CHE",
    "Coventry City": "COV",
    "Crystal Palace": "CRY",
    "Everton": "EVE",
    "Fulham": "FUL",
    "Hull City": "HUL",
    "Ipswich Town": "IPS",
    "Leeds United": "LEE",
    "Liverpool": "LIV",
    "Manchester City": "MCI",
    "Manchester United": "MUN",
    "Newcastle United": "NEW",
    "Nottingham Forest": "NOT",
    "Sunderland": "SUN",
    "Tottenham Hotspur": "TOT",
}

def get_team_id(club_name):
    abbr = CLUB_ABBR_MAP.get(club_name)
    if not abbr:
        return None
    res = supabase.table("teams").select("id").eq("abbreviation", abbr).eq("league", "EPL").single().execute()
    return res.data["id"] if res.data else None

PULSE_TO_SUPABASE_ABBR = {
    "ARS": "ARS", "AVL": "AVL", "BOU": "BOU", "BRE": "BRE",
    "BHA": "BHA", "CHE": "CHE", "COV": "COV", "CRY": "CRY",
    "EVE": "EVE", "FUL": "FUL", "HUL": "HUL", "IPS": "IPS",
    "LEE": "LEE", "LIV": "LIV", "MCI": "MCI", "MUN": "MUN",
    "NEW": "NEW", "NFO": "NOT", "SUN": "SUN", "TOT": "TOT",
}

def get_team_id_by_abbr(abbr):
    mapped = PULSE_TO_SUPABASE_ABBR.get(abbr)
    if not mapped:
        return None
    res = supabase.table("teams").select("id").eq("abbreviation", mapped).eq("league", "EPL").single().execute()
    return res.data["id"] if res.data else None

def fetch_player_details(player_id):
    url = f"https://footballapi.pulselive.com/football/players/{player_id}"
    try:
        r = requests.get(url, headers=PULSE_HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None

def build_player_record(details, p, team_id):
    if details:
        first_name = details.get("name", {}).get("first", "")
        last_name = details.get("name", {}).get("last", "")
        full_name = details.get("name", {}).get("display", "")
        position = POSITION_MAP.get(details.get("info", {}).get("position", ""), "")
        nationality = details.get("birth", {}).get("country", {}).get("country", "")
        height_cm = details.get("height")
        weight_kg = details.get("weight")
        player_id = details.get("playerId")
        headshot_url = f"https://resources.premierleague.com/premierleague25/photos/players/110x140/{player_id}.png" if player_id else None
    else:
        first_name = p["Name"].rsplit(" ", 1)[0] if " " in p["Name"] else ""
        last_name = p["Name"].rsplit(" ", 1)[1] if " " in p["Name"] else p["Name"]
        full_name = p["Name"]
        position = POSITION_MAP.get(p.get("Position", ""), "")
        nationality = p.get("Nationality", "")
        height_cm = None
        weight_kg = None
        headshot_url = None

    return {
        "league": "EPL",
        "team_id": team_id,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "position": position,
        "nationality": nationality,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "active": True,
        "headshot_url": headshot_url,
    }

def get_season():
    sid = int(epl.get_season_id())
    print(f"Using season ID: {sid} (2026/27)")
    return sid

def get_all_pl_clubs_ids(season_id):
    clubs = epl.get_club_ids(season_id)
    print(clubs)

def get_pl_players():
    season_id = get_season()

    # Get PL club pulselive IDs
    r = requests.get(f"https://footballapi.pulselive.com/football/compseasons/{season_id}/teams", headers=PULSE_HEADERS)
    pl_club_ids = {team["club"]["id"] for team in r.json()}

    # Get PL club pulselive ID -> abbreviation mapping
    club_id_to_abbr = {}
    for team in r.json():
        club = team.get("club", {})
        abbr = club.get("abbr")
        if abbr:
            club_id_to_abbr[club["id"]] = abbr

    # Step 1: Get players with team assigned (via eplda)
    players_df = epl.get_player_list(season_id)
    players_data = players_df.to_dict(orient="records")
    print(f"Players with team assigned: {len(players_data)}")

    seen_ids = set()
    player_records = []

    for i, p in enumerate(players_data):
        pid = p["ID"]
        seen_ids.add(int(pid))
        club_name = p["Current Team"]
        team_id = get_team_id(club_name)
        details = fetch_player_details(pid)
        player_records.append(build_player_record(details, p, team_id))

        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1}/{len(players_data)} players...")
            time.sleep(1)
        time.sleep(0.15)

    # Step 2: Get all players from season API and check null-team ones
    print("Checking null-team players...")
    null_team_ids = []
    for page in range(9):
        url = f"https://footballapi.pulselive.com/football/players?pageSize=100&page={page}&compSeasons={season_id}"
        r = requests.get(url, headers=PULSE_HEADERS)
        for p in r.json().get("content", []):
            ct = p.get("currentTeam", {})
            if not ct or ct.get("id") is None:
                pid = int(p["id"])
                if pid not in seen_ids:
                    null_team_ids.append(pid)

    print(f"Null-team players to check: {len(null_team_ids)}")

    extra_count = 0
    for i, pid in enumerate(null_team_ids):
        details = fetch_player_details(pid)
        if details:
            ct = details.get("currentTeam", {})
            if ct:
                club_id = ct.get("club", {}).get("id")
                if club_id in pl_club_ids:
                    abbr = club_id_to_abbr.get(club_id)
                    team_id = get_team_id_by_abbr(abbr) if abbr else None
                    name_display = details.get("name", {}).get("display", "")
                    p_fallback = {"ID": str(pid), "Name": name_display, "Position": "", "Nationality": "", "Current Team": ""}
                    player_records.append(build_player_record(details, p_fallback, team_id))
                    extra_count += 1

        if (i + 1) % 30 == 0:
            print(f"Checked null-team players: {i + 1}/{len(null_team_ids)}, found extra: {extra_count}")
            time.sleep(1)
        time.sleep(0.1)

    print(f"Extra players found from null-team check: {extra_count}")
    print(f"Total players: {len(player_records)}")

    # Clean existing EPL data, then insert
    supabase.table("players").delete().eq("league", "EPL").execute()

    print(f"Inserting {len(player_records)} players to Supabase...")
    response = supabase.table("players").upsert(player_records).execute()

    if response.data:
        print(f"Inserted: {len(response.data)}")
    else:
        print(f"Insert failed: {response}")

if __name__ == "__main__":
    get_pl_players()
