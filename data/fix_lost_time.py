import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO
from game_obj import open_game
from save_db import save_stage, save_tournament, get_recorded, update_teams, get_all, update_teams2

S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"

directory = "games"
# wanted_keys = ["participantID", "teamID", "goldStats", "championName", "playerName", "totalGold", "stats", "goldPerSecond"]

def grab_players():
    """ Function to grab all players"""
    player_list = {}
    with open('esports-data/players.json', 'rb') as file:
        players = json.load(file)
        for player in players:
            player_list[player['handle'].lower()] = {'id': player['player_id'], 'playerName': player['handle']}
    return player_list


def create_filtered_file(game_file, idx, start_date, player_list, tournament_id, stage_slug, game_name, teams):
    """ Function to grab events out of game file """
    event_10 = {}
    game_end = {}

    if not game_file:
        print(f'game obj not given {game_name}')
        return None
    for event in game_file:
        if event['eventType'] == 'game_end':
            game_end = event
        elif not event_10 and event["eventType"] == "stats_update" and event["gameTime"] > 600000 and event["gameTime"] < 1200000:
            event_10 = event
        if game_end and event_10:
            break

    return open_game(event_10, game_end, player_list, start_date, tournament_id, stage_slug, teams)
    

def download_gzip_and_write_to_json(file_name):
    # If file already exists locally do not re-download game
    if os.path.isfile(f"{file_name}.json"):
        return

    response = requests.get(f"{S3_BUCKET_URL}/{file_name}.json.gz")
    if response.status_code == 200:
        try:
            gzip_bytes = BytesIO(response.content)
            with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
            #     # with open(f"{file_name}.json", 'wb') as output_file:
            #     #     shutil.copyfileobj(gzipped_file, output_file)
                return json.load(gzipped_file)
            #     # print(f"{file_name}.json written")
        except Exception as e:
            print("Error:", e)
    else:
        print(f"Failed to download {file_name}")


def download_esports_files():
    directory = "esports-data"
    if not os.path.exists(directory):
        os.makedirs(directory)

    esports_data_files = ["leagues", "tournaments", "players", "teams", "mapping_data"]
    for file_name in esports_data_files:
        download_gzip_and_write_to_json(f"{directory}/{file_name}")


def download_games(player_list):
    start_time = time.time()
    with open("esports-data/tournaments.json", "r") as json_file:
        tournaments_data = json.load(json_file)
    with open("esports-data/mapping_data.json", "r") as json_file:
        mappings_data = json.load(json_file)

    if not os.path.exists(directory):
        os.makedirs(directory)

    mappings = {
        esports_game["esportsGameId"]: esports_game for esports_game in mappings_data
    } 

    game_counter = 0
    all_games_data = {}
    found = False
    # all_objs = get_all()
    for tournament in tournaments_data:
        # if tournament['slug'] == 'lcs_summer_2022':
        if tournament['slug'] == 'golden_league_opening_2023':
            found = True
        if found:
            start_date = tournament.get("startDate", "")
            print(f"Processing {tournament['slug']}")
            for stage in tournament["stages"]:
                save_stage_data = []
                for section in stage["sections"]:
                    for match in section["matches"]:
                        # update team_id into dict then save
                        for game in match["games"]:
                            if game["state"] == "completed":
                                try:
                                    platform_game_id = mappings[game["id"]]["platformGameId"]
                                except KeyError:
                                    print(f"{platform_game_id} {game['id']} not found in the mapping table")
                                    continue
                                
                                file_to_download = f"{directory}/{platform_game_id}"
                                game_file = download_gzip_and_write_to_json(file_to_download)
                                # create_filtered_file(game_file, game_counter, start_date, player_list, tournament['id'], stage['slug'], platform_game_id, all_objs)
                        #         update_teams2(game_file, tournament['id'], match['teams'], missing_players, player_list)
                # save into db (missing team_id, lost_time incorrect)
                #         if match["state"] == "completed":
                #             for team in match["teams"]:
                #                 if team['players']:
                #                     team_id = team["id"]
                #                     players = team["players"]
                #                     update_teams(team_id, players, tournament['id'], all_objs, missing_players)

                                save_obj = create_filtered_file(game_file, game_counter, start_date, player_list, tournament['id'], stage['slug'], platform_game_id, match["teams"])
                                if save_obj:
                                    save_stage_data.append(save_obj)
                                game_counter += 1

                            if game_counter % 10 == 0:
                                print(
                                    f"----- Processed {game_counter} games, current run time: \
                                    {round((time.time() - start_time)/60, 2)} minutes"
                                )
                save_stage(save_stage_data)
                # save_tournament(tournament['id'], tournament['slug'])


if __name__ == "__main__":
    download_esports_files()
    player_list = grab_players()
    download_games(player_list)

