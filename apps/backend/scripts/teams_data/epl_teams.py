import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from dotenv import load_dotenv, find_dotenv
from components.supabase import supabase

load_dotenv(find_dotenv())

API_KEY = os.getenv("FOOTBALL_KEY")

url = "https://api.football-data.org/v4/competitions/PL/teams"

headers = {
    "X-Auth-Token": API_KEY
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"Failed: {response.status_code}")
    print(response.text)
    exit()

data = response.json()

teams = []

for item in data["teams"]:
    teams.append({
        "league": "EPL",
        "name": item["name"],
        "city": item["area"]["name"],
        "abbreviation": item.get("tla", "N/A"),
        "logo_url": item.get("crest")
    })

if teams:
    result = supabase.table("teams").insert(teams).execute()

    print("Inserted/updated teams:", len(teams))
else:
    print("No teams returned")