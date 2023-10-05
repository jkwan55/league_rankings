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
