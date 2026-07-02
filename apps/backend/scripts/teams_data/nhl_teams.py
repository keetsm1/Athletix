import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from components.supabase import supabase

url = 'https://api-web.nhle.com/v1/standings/2026-04-17'

response = requests.get(url)

if response.status_code == 200:
     data = response.json()
else:
     print("Failed to get data")


teams = []

for team in data["standings"]:
     teams.append({
          "league": "NHL",
          "name": team["teamName"]["default"],
          "city": team["placeName"]["default"],
          "abbreviation": team["teamAbbrev"]["default"],
          "logo_url": team["teamLogo"]
     })

result = supabase.table("teams").insert(teams).execute()


    
