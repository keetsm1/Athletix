import os
import sys
import time

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from components.supabase import supabase

TEAM_ABBREVIATIONS = [
    "ANA", "BOS", "BUF", "CGY", "CAR", "CHI", "COL", "CBJ",
    "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NSH",
    "NJD", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS", "SEA",
    "STL", "TBL", "TOR", "UTA", "VAN", "VGK", "WSH", "WPG",
]

SEASONS = ["20242025", "20252026"]


def to_seconds(toi_str: str) -> int:
    parts = toi_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def get_boxscore(game_id: int, player_map: dict, team_map: dict):
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed for {game_id} | {response.status_code} | {response.text}")
        return []

    data = response.json()
    game_date = data["gameDate"]
    season = str(data["season"])

    records = []

    for side in ("awayTeam", "homeTeam"):
        team_data = data["playerByGameStats"][side]
        team_abbrev = data[side]["abbrev"]
        team_id = team_map.get(team_abbrev)

        if not team_id:
            print(f"  Team {team_abbrev} not found in DB, skipping")
            continue

        for group in ("forwards", "defense", "goalies"):
            for player in team_data.get(group, []):
                nhl_id = player["playerId"]
                player_id = player_map.get(nhl_id)

                if not player_id:
                    print(f"  Player {nhl_id} ({player['name']['default']}) not found in DB, skipping")
                    continue

                toi_seconds = to_seconds(player["toi"]) if player.get("toi") else 0

                records.append({
                    "player_id": player_id,
                    "team_id": team_id,
                    "game_id": str(game_id),
                    "game_date": game_date,
                    "season": season,
                    "position": player.get("position"),
                    "goals": player.get("goals", 0),
                    "assists": player.get("assists", 0),
                    "points": player.get("points", 0),
                    "shots": player.get("sog", 0),
                    "power_play_goals": player.get("powerPlayGoals", 0),
                    "power_play_assists": player.get("powerPlayAssists", 0),
                    "hits": player.get("hits", 0),
                    "blocked_shots": player.get("blockedShots", 0),
                    "plus_minus": player.get("plusMinus", 0),
                    "penalty_minutes": player.get("pim", 0),
                    "time_on_ice": toi_seconds,
                })

    return records


def main():
    player_resp = supabase.table("players") \
        .select("id,nhl_player_id") \
        .eq("league", "NHL") \
        .execute()
    player_map = {row["nhl_player_id"]: row["id"] for row in (player_resp.data or [])}
    print(f"Loaded {len(player_map)} player mappings")

    team_resp = supabase.table("teams") \
        .select("id,abbreviation") \
        .eq("league", "NHL") \
        .execute()
    team_map = {row["abbreviation"]: row["id"] for row in (team_resp.data or [])}
    print(f"Loaded {len(team_map)} team mappings")

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

            time.sleep(0.1)

    print(f"Found {len(game_ids)} unique game IDs")

    total_inserted = 0
    total_updated = 0

    for i, game_id in enumerate(game_ids):
        records = get_boxscore(game_id, player_map, team_map)
        if not records:
            continue

        existing = supabase.table("nhl_player_game_stats") \
            .select("id,player_id") \
            .eq("game_id", str(game_id)) \
            .execute()
        existing_player_ids = {row["player_id"] for row in (existing.data or [])}

        to_insert = [r for r in records if r["player_id"] not in existing_player_ids]
        to_update = [r for r in records if r["player_id"] in existing_player_ids]

        if to_insert:
            supabase.table("nhl_player_game_stats").insert(to_insert).execute()
            total_inserted += len(to_insert)

        if to_update:
            for r in to_update:
                supabase.table("nhl_player_game_stats") \
                    .update(r) \
                    .eq("game_id", r["game_id"]) \
                    .eq("player_id", r["player_id"]) \
                    .execute()
            total_updated += len(to_update)

        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{len(game_ids)} games...")

        time.sleep(0.15)

    print(f"Done. Inserted: {total_inserted}, Updated: {total_updated}")


if __name__ == "__main__":
    main()
