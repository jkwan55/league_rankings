import sys
import os
import django

sys.path.append('../backend/league_data')
os.environ['DJANGO_SETTINGS_MODULE'] = 'league_data.settings'
django.setup()

from data.models import PlayerStats, RecordedTournaments


def save_tournament(tournament_id, tournament_name):
    RecordedTournaments.objects.create(tournament_id=tournament_id, tournament_name=tournament_name)


def get_recorded():
    return RecordedTournaments.objects.all()


def get_all():
    return PlayerStats.objects.all()


def update_teams(team_id, players, tournament_id, all_objs, missing_players):
    # needs to check and remove from list, but wip
    for player in players:
        if 'id' in player and (tournament_id, player['id']) in missing_players:
            print('found', player['id'])
            filtered_objs = all_objs.filter(tournament_id=tournament_id, player_id=player['id'])
            filtered_objs.update(team_id=team_id)
            if 'role' in player:
                filtered_objs.update(role=player['role'])


def update_teams2(game_file, tournament_id, teams, missing_players, player_list):
    
    event_update = {}

    if not game_file:
        print(f'game obj not given {game_name}')
        return None
    for event in game_file:
        if event["eventType"] == "stats_update":
            event_update = event
            break

    participants = event_update['participants']
    for participant in participants:
        name = ''
        if 'playerName' in participant:
            name = participant['playerName'].split(" ")
        elif 'summonerName' in participant:
            name = participant['summonerName'].split(" ")
        else:
            pass
        if len(name) > 1:
            name = name[1:]
        name = ' '.join(name).lower()
        if name in player_list:
            player_id = player_list[name]['id']
            if (tournament_id, player_id) in missing_players:
                update_player = PlayerStats.objects.filter(tournament_id=tournament_id, player_id=player_id, team_id__isnull=True)
                if update_player:
                    if participant['teamID']:
                        update_player.update(team_id=teams[0]["id"])
                        # print('blue',teams[0]['id'])
                    else:
                        # print('red',teams[1]['id'])
                        update_player.update(team_id=teams[1]["id"])



def save_stage(stage_data):
    new_obj = {}
    do_once = ['tournament_id', 'stage_slug', 'player_name', 'player_id', 'start_date']

    for player_data in stage_data:
        for player_id in player_data:
            if player_id in new_obj:
                for key in player_data[player_id]:
                    if key not in do_once:
                        new_obj[player_id][key] = player_data[player_id][key] + new_obj[player_id][key] if key in new_obj[player_id] else 0
            else:
                new_obj[player_id] = player_data[player_id]

    #save to db
    save_into_db = [PlayerStats(
        start_date = new_obj[player_id]['start_date'] if 'start_date' in new_obj[player_id] else '',
        tournament_id = new_obj[player_id]['tournament_id'] if 'tournament_id' in new_obj[player_id] else 0,
        stage_slug = new_obj[player_id]['stage_slug'] if 'stage_slug' in new_obj[player_id] else '',
        player_id = new_obj[player_id]['player_id'] if 'player_id' in new_obj[player_id] else 0,
        player_name = new_obj[player_id]['player_name'] if 'player_name' in new_obj[player_id] else '',
        gold_10 = new_obj[player_id]['gold_10'] if 'gold_10' in new_obj[player_id] else 0,
        gold_10_count = new_obj[player_id]['gold_10_count'] if 'gold_10_count' in new_obj[player_id] else 0,
        tower_delta_10 = new_obj[player_id]['tower_delta_10'] if 'tower_delta_10' in new_obj[player_id] else 0,
        tower_delta_10_count = new_obj[player_id]['tower_delta_10_count'] if 'tower_delta_10_count' in new_obj[player_id] else 0,
        gold_20 = new_obj[player_id]['gold_20'] if 'gold_20' in new_obj[player_id] else 0,
        gold_20_count = new_obj[player_id]['gold_20_count'] if 'gold_20_count' in new_obj[player_id] else 0,
        tower_delta_20 = new_obj[player_id]['tower_delta_20'] if 'tower_delta_20' in new_obj[player_id] else 0,
        tower_delta_20_count = new_obj[player_id]['tower_delta_20_count'] if 'tower_delta_20_count' in new_obj[player_id] else 0,
        win_time = new_obj[player_id]['win_time'] if 'win_time' in new_obj[player_id] else 0,
        win_count = new_obj[player_id]['win_count'] if 'win_count' in new_obj[player_id] else 0,
        lost_time = new_obj[player_id]['lost_time'] if 'lost_time' in new_obj[player_id] else 0,
        lost_count = new_obj[player_id]['lost_count'] if 'lost_count' in new_obj[player_id] else 0 
    ) for player_id in new_obj]

    PlayerStats.objects.bulk_create(save_into_db)
