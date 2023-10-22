import os
import json

# commented out lines may be for low memory VMs

# def open_game():
def open_game(event_10, event_20, game_end, player_list, start_date, tournament_id, stage_slug, team_ids):
    """Function to open games and put into database"""

    # add tournament and startDate to keep track of time
    all_game_data = {}
    # prefix_games = set([game.split('_')[0] for game in os.listdir("games")])

    # grab all players
    # player_list = {}
    # with open('esports-data/players.json', 'rb') as file:
    #     players = json.load(file)
    #     for player in players:
    #         player_list[player['handle'].lower()] = {'id': player['player_id'], 'playerName': player['handle']}
        
    def game_updates(obj, time, teams, missing_end, start_date, tournament_id, stage_slug, player_list, team_ids):
        # if missing_end:
        #     teams = {}
        #     teams[100] = {}
        #     teams[200] = {}
        blue_team = team_ids[0] if team_ids[0]["side"] == "blue" else team_ids[1]
        red_team = team_ids[0] if team_ids[0]["side"] == "red" else team_ids[1]

        # grab tower stats
        for team in obj['teams']:
            teams[team['teamID']][f'towerKills{time}'] = team['towerKills']
        blue_towers = teams[100][f'towerKills{time}']
        delta_towers = teams[200][f'towerKills{time}'] - blue_towers
        teams[100][f'tower_delta_{time}'] = -1 * delta_towers
        teams[200][f'tower_delta_{time}'] = delta_towers

        # grab individual performances
        participants = obj['participants']
        game_id = obj['platformGameId']
        for participant in participants:
            team_id = blue_team["id"] if participant['teamID'] == 100 else red_team["id"]
            name = ''
            if 'playerName' in participant:
                name = participant['playerName'].split(" ")
            elif 'summonerName' in participant:
                name = participant['summonerName'].split(" ")
            else:
                print(f'unknown player key in dict')
                with open(f'unknown_dict/{game_id}_{time}.json', 'a') as unknown_dict_key:
                    unknown_dict_key.write(json.dumps(obj))
                    continue
            if len(name) > 1:
                name = name[1:]
            name = ' '.join(name).lower()
            if name not in player_list:
                print(f'name not found {name}')
                with open(f'games/{game_id}_update_{time}_{name}.json', 'a') as unknown_name_file:
                    unknown_name_file.write(json.dumps(obj))
                    continue
            player_id = player_list[name]['id']
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
                    if 'winner' in teams[participant['teamID']] and teams[participant['teamID']]['winner']:
                        all_game_data[player_id]['win_time'] = \
                            teams[participant['teamID']]['gameTime'] + (all_game_data[player_id]['win_time'] \
                                if 'win_time' in all_game_data[player_id] else 0)

                        all_game_data[player_id]['win_count'] = \
                            1 + (all_game_data[player_id]['win_count'] \
                                if 'win_count' in all_game_data[player_id] else 0)
                        
                    # do the same for lost games
                    elif 'winner' in teams[participant['teamID']] and not teams[participant['teamID']]['winner']:
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
                all_game_data[player_id]['player_name'] = name
                all_game_data[player_id]['player_id'] = player_id
                all_game_data[player_id]['team_id'] = team_id
                all_game_data [player_id][f'gold_{time}'] = participant['totalGold']
                all_game_data[player_id][f'gold_{time}_count'] = 1
                all_game_data[player_id][f'tower_delta_{time}'] = teams[participant['teamID']][f'tower_delta_{time}']
                all_game_data[player_id][f'tower_delta_{time}_count'] = 1
                if time == 10 and not missing_end:
                    if 'winner' in teams[participant['teamID']] and teams[participant['teamID']]['winner']:
                        all_game_data[player_id]['win_time'] = teams[participant['teamID']]['gameTime']
                        all_game_data[player_id]['win_count'] = 1
                    elif 'winner' in teams[participant['teamID']] and not teams[participant['teamID']]['winner']:
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
        game_updates(event_10, 10, teams, False if game_end else True, start_date, tournament_id, stage_slug, player_list, team_ids)
    if event_20:
        game_updates(event_20, 20, teams, False if game_end else True, start_date, tournament_id, stage_slug, player_list, team_ids)
    
    return all_game_data

    # for game in prefix_games:
    #     teams = {}
    #     missing_end = False
    #     if os.path.exists(f'games/{game}_gameend.json'):
    #         with open(f'games/{game}_gameend.json', 'rb') as file:
    #             end = json.load(file)
    #             # grab winning team
    #             # get time to win/lose
    #             teams[end['winningTeam']] = {'gameTime': end['gameTime'], 'winner': True}
    #             if end['winningTeam'] == 100:
    #                 teams[200] = {'gameTime': end['gameTime'], 'winner': False}
    #             else:
    #                 teams[100] = {'gameTime': end['gameTime'], 'winner': False}
    #     else:
    #         missing_end = True
    #         print(f'missing gameend for {game}')

    #     if os.path.exists(f'games/{game}_update10.json'):
    #         with open(f'games/{game}_update10.json', 'rb') as file:
    #             obj = json.load(file)
    #             game_updates(obj, 10, teams, missing_end)

    #     if os.path.exists(f'games/{game}_update20.json'):
    #         with open(f'games/{game}_update20.json', 'rb') as file:
    #             obj = json.load(file)
    #             game_updates(obj, 20, teams, missing_end)
    #             file.close()

                # GRAB ONE TOURNAMENT AT A TIME AND ADD TO DICTIONARY
                # GRAB TIME OF START OR END OF TOURNAMENT
                # SAVE INTO DATABASE ONE TOURNAMENT AT A TIME


if __name__ == "__main__":
    open_games()