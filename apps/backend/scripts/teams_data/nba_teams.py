import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from components.supabase import supabase
from nba_api.stats.static import teams

nba_teams = teams.get_teams()

teams = []

for team in nba_teams:
    teams.append({
        "league": "NBA",
        "name" : team["nickname"],
        "city": team["city"],
        "abbreviation": team["abbreviation"],
        "logo_url": "N/A"
    })

result = supabase.table("teams").insert(teams).execute()