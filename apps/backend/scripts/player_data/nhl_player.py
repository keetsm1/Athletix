import requests
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from components.supabase import supabase

team_abbreviations = [
    "ANA", "BOS", "BUF", "CGY", "CAR", "CHI", "COL", "CBJ",
    "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NSH",
    "NJD", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS", "SEA",
    "STL", "TBL", "TOR", "UTA", "VAN", "VGK", "WSH", "WPG"
]

players = []

for team in team_abbreviations:

    url = f"https://api-web.nhle.com/v1/roster/{team}/current"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed for {team} | {response.status_code} | {response.text}")
        continue

    data = response.json()

    team_res = supabase.table("teams") \
                .select("id") \
                .eq("abbreviation", team) \
                .eq("league", "NHL")\
                .single() \
                .execute()
    team_id = team_res.data["id"] if team_res.data else None

    for player in data["forwards"]:
        players.append({
            "league": "NHL",
            "team_id": team_id,
            "nhl_player_id": player["id"],
            "first_name": player["firstName"]["default"],
            "last_name": player["lastName"]["default"],
            "full_name": player["firstName"]["default"] + " " + player["lastName"]["default"],
            "position": player["positionCode"],
            "nationality": player["birthCountry"],
            "height_cm": player["heightInCentimeters"],
            "weight_kg": player["weightInKilograms"],
            "headshot_url": player["headshot"],
        })

    for player in data["defensemen"]:
            players.append({
            "league": "NHL",
            "team_id": team_id,
            "nhl_player_id": player["id"],
            "first_name": player["firstName"]["default"],
            "last_name": player["lastName"]["default"],
            "full_name": player["firstName"]["default"] + " " + player["lastName"]["default"],
            "position": player["positionCode"],
            "nationality": player["birthCountry"],
            "height_cm": player["heightInCentimeters"],
            "weight_kg": player["weightInKilograms"],
            "headshot_url": player["headshot"],
        })

    for player in data["goalies"]:
            players.append({
            "league": "NHL",
            "team_id": team_id,
            "nhl_player_id": player["id"],
            "first_name": player["firstName"]["default"],
            "last_name": player["lastName"]["default"],
            "full_name": player["firstName"]["default"] + " " + player["lastName"]["default"],
            "position": player["positionCode"],
            "nationality": player["birthCountry"],
            "height_cm": player["heightInCentimeters"],
            "weight_kg": player["weightInKilograms"],
            "headshot_url": player["headshot"],
        })

    time.sleep(0.2)

nhl_ids = [p["nhl_player_id"] for p in players]

existing = supabase.table("players") \
    .select("id,nhl_player_id") \
    .in_("nhl_player_id", nhl_ids) \
    .execute()

id_map = {row["nhl_player_id"]: row["id"] for row in (existing.data or [])}

to_update = []
to_insert = []

for p in players:
    if p["nhl_player_id"] in id_map:
        p["id"] = id_map[p["nhl_player_id"]]
        to_update.append(p)
    else:
        to_insert.append(p)

if to_update:
    for p in to_update:
        supabase.table("players").update({k: v for k, v in p.items() if k != "id"}).eq("id", p["id"]).execute()

if to_insert:
    response = supabase.table("players").insert(to_insert).execute()
    print("Inserted:", len(response.data or []))

if to_update:
    print("Updated:", len(to_update))