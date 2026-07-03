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

response = supabase.table("players").upsert(players).execute()

if response.data:
    print("Inserted:", len(response.data))
else:
    print("Insert failed:", response)