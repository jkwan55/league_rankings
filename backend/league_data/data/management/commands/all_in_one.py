import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO
from data.models import PlayerStats
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Grab tournaments and save into db"


    def handle(self, *args, **options):
        S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"
        directory = "games"

        def grab_players():
            """ Function to grab all players"""
            player_list = {}
            with open('esports-data/players.json', 'rb') as file:
                players = json.load(file)
                for player in players:
                    player_list[player['handle'].lower()] = {'id': player['player_id'], 'playerName': player['handle']}
            return player_list


        def create_filtered_file(game_file, idx, start_date, player_list, tournament_id, stage_slug):
            """ Condense json into single events """
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


        def open_game(event_10, event_20, game_end, player_list, start_date, tournament_id, stage_slug):
            """Function to open games and put into database"""

            # add tournament and startDate to keep track of time
            all_game_data = {}

            def game_updates(obj, time, teams, missing_end, start_date, tournament_id, stage_slug):
                # grab tower stats
                for team in obj['teams']:
                    teams[team['teamID']][f'towerKills{time}'] = team['towerKills']
                blue_towers = teams[100][f'towerKills{time}']
                delta_towers = teams[200][f'towerKills{time}'] - blue_towers
                teams[100][f'tower_delta_{time}'] = -1 * delta_towers
                teams[200][f'tower_delta_{time}'] = delta_towers

                # grab individual performances
                participants = obj['participants']
                for participant in participants:
                    name = participant['playerName'].split(" ")
                    if len(name) > 1:
                        name = name[1:]
                    name = ' '.join(name)
                    player_id = player_list[name.lower()]['id']
                    if player_id in all_game_data:
                        # add time of tournament for game
                        all_game_data[player_id]['start_date'] = start_date
                        all_game_data[player_id]['tournament_id'] = tournament_id
                        all_game_data[player_id]['stage_slug'] = stage_slug

                        # check if player exists with totalGold at 10/20
                        all_game_data[player_id][f'gold_{time}'] = \
                            participant['totalGold'] + (all_game_data[player_id][f'gold_{time}']\
                                if f'gold_{time}' in all_game_data[player_id] else 0)

                        # check if player exists with games counted at 10/20
                        all_game_data[player_id][f'gold_{time}_count'] = \
                            1 + (all_game_data[player_id][f'gold_{time}_count'] \
                                if f'gold_{time}_count' in all_game_data[player_id] else 0)

                        # check if player exists with towerDelta at 10/20
                        all_game_data[player_id][f'tower_delta_{time}'] = \
                            teams[participant['teamID']][f'tower_delta_{time}'] + (all_game_data[player_id][f'tower_delta_{time}'] \
                                if f'tower_delta_{time}' in all_game_data[player_id] else 0)

                        # check if player exists with towerDelta count at 10/20
                        all_game_data[player_id][f'tower_delta_{time}_count'] = \
                            1 + (all_game_data[player_id][f'tower_delta_{time}_count'] \
                                if f'tower_delta_{time}_count' in all_game_data[player_id] else 0)
                        
                        # make sure to calculate win and lose time only once, some games dont last 20mins
                        if time == 10 and not missing_end:
                            # add win_time and count for Win Rate
                            if 'winner' in teams[participant['teamID']]:
                                all_game_data[player_id]['win_time'] = \
                                    teams[participant['teamID']]['gameTime'] + (all_game_data[player_id]['win_time'] \
                                        if 'win_time' in all_game_data[player_id] else 0)

                                all_game_data[player_id]['win_count'] = \
                                    1 + (all_game_data[player_id]['win_count'] \
                                        if 'win_count' in all_game_data[player_id] else 0)
                                
                            # do the same for lost games
                            else:
                                all_game_data[player_id]['lost_time'] = \
                                    teams[participant['teamID']]['gameTime'] + (all_game_data[player_id]['lost_time'] \
                                        if 'lost_time' in all_game_data[player_id] else 0)
                                        
                                all_game_data[player_id]['lost_count'] = \
                                    1 + (all_game_data[player_id]['lost_count'] \
                                        if 'lost_count' in all_game_data[player_id] else 0)
                    else:
                        all_game_data[player_id] = {}
                        all_game_data[player_id]['start_date'] = start_date
                        all_game_data[player_id]['tournament_id'] = tournament_id
                        all_game_data[player_id]['stage_slug'] = stage_slug
                        all_game_data[player_id]['player_name'] = participant['playerName']
                        all_game_data[player_id]['player_id'] = player_id
                        all_game_data [player_id][f'gold_{time}'] = participant['totalGold']
                        all_game_data[player_id][f'gold_{time}_count'] = 1
                        all_game_data[player_id][f'tower_delta_{time}'] = teams[participant['teamID']][f'tower_delta_{time}']
                        all_game_data[player_id][f'tower_delta_{time}_count'] = 1
                        if time == 10 and not missing_end:
                            if 'winner' in teams[participant['teamID']]:
                                all_game_data[player_id]['win_time'] = teams[participant['teamID']]['gameTime']
                                all_game_data[player_id]['win_count'] = 1
                            else:
                                all_game_data[player_id]['lost_time'] = teams[participant['teamID']]['gameTime']
                                all_game_data[player_id]['lost_count'] = 1

            teams = {}
            if game_end:
                teams[game_end['winningTeam']] = {'gameTime': game_end['gameTime'], 'winner': True}
                if game_end['winningTeam'] == 100:
                    teams[200] = {'gameTime': game_end['gameTime'], 'winner': False}
                else:
                    teams[100] = {'gameTime': game_end['gameTime'], 'winner': False}
            else:
                teams[100] = {}
                teams[200] = {}
            if event_10:
                game_updates(event_10, 10, teams, False if game_end else True, start_date, tournament_id, stage_slug)
            if event_20:
                game_updates(event_20, 20, teams, False if game_end else True, start_date, tournament_id, stage_slug)
            
            print(all_game_data)
            return all_game_data


        def save_stage(stage_data):
            """ Save game data per tournament into database """ 
            new_obj = {}
            do_once = ['tournament_id', 'stage_slug', 'playerName', 'start_date']

            for player_data in stage_data:
                for player_id in player_data:
                    if player_id in new_obj:
                        for key in player_data[player_id]:
                            if key not in do_once:
                                new_obj[player_id][key] = new_obj[player_id][key] + player_data[player_id][key]
                    else:
                        new_obj[player_id] = player_data[player_id]

            #save to db
            save_into_db = [PlayerStats(
                start_date = new_obj[player_id]['start_date'],
                tournament_id = new_obj[player_id]['tournament_id'],
                stage_slug = new_obj[player_id]['stage_slug'],
                player_id = new_obj[player_id]['player_id'],
                player_name = new_obj[player_id]['player_name'],
                gold_10 = new_obj[player_id]['gold_10'],
                gold_10_count = new_obj[player_id]['gold_10_count'],
                tower_delta_10 = new_obj[player_id]['tower_delta_10'],
                tower_delta_10_count = new_obj[player_id]['tower_delta_10_count'],
                gold_20 = new_obj[player_id]['gold_20'],
                gold_20_count = new_obj[player_id]['gold_20_count'],
                tower_delta_20 = new_obj[player_id]['tower_delta_20'],
                tower_delta_20_count = new_obj[player_id]['tower_delta_20_count'],
                win_time = new_obj[player_id]['win_time'],
                win_count = new_obj[player_id]['win_count'],
                lost_time = new_obj[player_id]['lost_time'],
                lost_count = new_obj[player_id]['lost_count'] 
            ) for player_id in new_obj]

            PlayerStats.objects.bulk_create(save_into_db)


        def download_gzip_and_write_to_json(file_name):
            # If file already exists locally do not re-download game
            if os.path.isfile(f"{file_name}.json"):
                return

            response = requests.get(f"{S3_BUCKET_URL}/{file_name}.json.gz")
            if response.status_code == 200:
                try:
                    gzip_bytes = BytesIO(response.content)
                    with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
                        return json.load(gzipped_file)
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
                    if tournament['slug'] == 'lcs_summer_2022': #or tournament['slug'] == 'lcs_summer_2023':
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

        download_esports_files()
        player_list = grab_players()
        download_games(player_list)

