import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO
from save_into_db import open_game


S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"

directory = "games"
wanted_keys = ["participantID", "teamID", "goldStats", "championName", "playerName", "totalGold", "stats", "goldPerSecond"]

def grab_players():
    """ Function to grab all players"""
    player_list = {}
    with open('esports-data/players.json', 'rb') as file:
        players = json.load(file)
        for player in players:
            player_list[player['handle'].lower()] = {'id': player['player_id'], 'playerName': player['handle']}
    return player_list

def create_filtered_file(game_file, idx, start_date, player_list, tournament_id, stage_slug):
    event_10 = {}
    event_20 = {}
    game_end = {}

    for event in game_file:
        if event['eventType'] == 'game_end':
            game_end = event
        elif not event_10 and event["eventType"] == "stats_update" and event["gameTime"] > 600000 and event["gameTime"] < 1200000:
            event_10 = event
        elif not event_20 and event["eventType"] == "stats_update" and event["gameTime"] > 1200000:
            event_20 = event
        if event_10 and event_20 and game_end:
            break

    return open_game(event_10, event_20, game_end, player_list, start_date, tournament_id, stage_slug)
    
    # FOR LOW MEMORY VMs: read character a time in case memory load is too high
    """
        found_10 = False
        found_20 = False
        end_found = False
        current_object = ""
        start = 0
        
        for char in file.read():
            if char == '{':
                start += 1
            elif char == '}':
                start -= 1
            current_object += char
            if start == 0 and len(current_object) < 2:
                current_object = ""
            elif start == 0 :
                obj = json.loads(current_object)
                if obj["eventType"] == "game_end":
                    ge = open("games/game" + str(idx) + "_gameend.json", "a")
                    ge.write(current_object)
                    ge.close()
                    print(filename, "game end created")
                elif not found_10 and obj["eventType"] == "stats_update" and obj["gameTime"] > 600000:
                    update10 = open("games/game" + str(idx) + "_update10.json", "a")

                    p = obj['participants']
                    new_list = []
                    for participant in p:
                        new_dict = {key: participant[key] for key in wanted_keys}
                        new_list.append(new_dict)
                    obj['participants'] = new_list
                    new_obj = json.dumps(obj)

                    update10.write(new_obj)
                    update10.close()
                    found_10 = True
                    print(filename, "update 10 created")
                elif not found_20 and obj["eventType"] == "stats_update" and obj["gameTime"] > 1200000:
                    update20 = open("games/game" + str(idx) + "_update20.json", "a")

                    p = obj['participants']
                    new_list = []
                    for participant in p:
                        new_dict = {key: participant[key] for key in wanted_keys}
                        new_list.append(new_dict)
                    obj['participants'] = new_list
                    new_obj = json.dumps(obj)

                    update20.write(new_obj)
                    update20.close()
                    found_20 = True
                    print(filename, "update 20 created")
                current_object = ""
    """


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
    for tournament in tournaments_data:
        start_date = tournament.get("startDate", "")
        if start_date.startswith(str(2022)) or start_date.startswith(str(2023)):
            if tournament['slug'] == 'lcs_summer_2022' or tournament['slug'] == 'lcs_summer_2023':
                print(f"Processing {tournament['slug']}")
                for stage in tournament["stages"]:
                    save_stage_data = []
                    for section in stage["sections"]:
                        for match in section["matches"]:
                            for game in match["games"]:
                                if game["state"] == "completed":
                                    try:
                                        platform_game_id = mappings[game["id"]]["platformGameId"]
                                    except KeyError:
                                        print(f"{platform_game_id} {game['id']} not found in the mapping table")
                                        continue
                                    
                                    file_to_download = f"{directory}/{platform_game_id}"
                                    game_file = download_gzip_and_write_to_json(file_to_download)                                    
                                    save_stage_data.append(create_filtered_file(game_file, game_counter, start_date, player_list, tournament['id'], stage['slug']))
                                    game_counter += 1

                                if game_counter % 10 == 0:
                                    print(
                                        f"----- Processed {game_counter} games, current run time: \
                                        {round((time.time() - start_time)/60, 2)} minutes"
                                    )
                    save_into_db(save_stage_data)



if __name__ == "__main__":
    download_esports_files()
    player_list = grab_players()
    download_games(player_list)

