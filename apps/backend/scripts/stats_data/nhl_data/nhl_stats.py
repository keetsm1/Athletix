import os
import sys

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

TEAM_ABBREVIATIONS = [
    "ANA", "BOS", "BUF", "CGY", "CAR", "CHI", "COL", "CBJ",
    "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NSH",
    "NJD", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS", "SEA",
    "STL", "TBL", "TOR", "UTA", "VAN", "VGK", "WSH", "WPG",
]

SEASONS = ["20242025", "20252026"]

def get_boxscore(game_id):
    for game in game_id:
        url = f'https://api-web.nhle.com/v1/gamecenter/game_id/boxscore'

        response = request.get(url)

        if response.status_code != 200:
            print(f"Failed for {game}| {response.status_code} | {response.text}")
            continue 

        #data points we need for the table:
        # id, player_id (from players table), team_id (from teams table), gameId, game_date, season, position, goals, assists, points, 
        # shots, pp goals, pp assists, hits, blocked shots, +-, pen mins, TOI.      
        #we can find all this data by looking in the playerByGameStats section of the box score URL.

def main() -> None:
    game_ids: set[int] = set()

    for team in TEAM_ABBREVIATIONS:
        for season in SEASONS:
            url = f"https://api-web.nhle.com/v1/club-schedule-season/{team}/{season}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Failed for {team} ({season}) | {response.status_code} | {response.text}")
                continue

            for game in response.json()["games"]:
                game_ids.add(game["id"])

    print(game_ids)


if __name__ == "__main__":
    main()