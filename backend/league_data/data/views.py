from django.shortcuts import render
from rest_framework import viewsets
from .serializers import PlayerStatsSerializer
from .models import PlayerStats
from django.views import View
from django.http import HttpResponse, JsonResponse
import json
from datetime import date
from dateutil.relativedelta import relativedelta

# Create your views here.

# [0] -> 'AVG_GOLD_10_WEIGHT'
# [1] -> 'AVG_GOLD_20_WEIGHT'
# [2] -> 'AVG_TOWER_DELTA_10_WEIGHT'
# [3] -> 'AVG_TOWER_DELTA_20_WEIGHT'
# [4] -> 'WIN_RATE_WEIGHT'
# [5] -> 'AVG_WIN_TIME_WEIGHT'
#[6] -> 'AVG_LOST_TIME_WEIGHT'
weights = [60.850482067668835, -81.86179372351509, 22.915557140713318, 25.515510378538025, -9.376862747866605, -4.006092027320668, 2.1338514352977596]

# grab min and max from find_max_min, hard code for now, running out of time
min_avg_gold_10 = 2068.6666666666665
max_avg_gold_10 = 4515.9
min_avg_gold_20 = 4281.222222222223
max_avg_gold_20 = 9236.6
min_tower_delta_10 = -0.5
max_tower_delta_10 = 1.0
min_tower_delta_20 = -5.5
max_tower_delta_20 = 7.0
min_total_win = 0 # no longer used
max_total_win = 376 # no longer used
min_total_lost = 0 # no longer used
max_total_lost = 323 # no longer used
min_win_time = 1166432.0
max_win_time = 3423385.0
min_lost_time = 1260949.0
max_lost_time = 2733361.0

def normalize(target, min_val, max_val):
    return ( target - min_val ) / ( max_val - min_val )

def compute_weights(queryset):
    team_dict = {}
    for player_stats in queryset:
        team_name = player_stats.team_name
        if team_name in team_dict:
            team_dict[team_name]['gold_10_total'] = team_dict[team_name]['gold_10_total'] + player_stats.gold_10
            team_dict[team_name]['gold_10_count'] = team_dict[team_name]['gold_10_count'] + player_stats.gold_10_count
            team_dict[team_name]['gold_20_total'] = team_dict[team_name]['gold_20_total'] + player_stats.gold_20
            team_dict[team_name]['gold_20_count'] = team_dict[team_name]['gold_20_count'] + player_stats.gold_20_count
            team_dict[team_name]['tower_delta_10_total'] = team_dict[team_name]['tower_delta_10_total'] + player_stats.tower_delta_10
            team_dict[team_name]['tower_delta_10_count'] = team_dict[team_name]['tower_delta_10_count'] + player_stats.tower_delta_10_count
            team_dict[team_name]['tower_delta_20_total'] = team_dict[team_name]['tower_delta_20_total'] + player_stats.tower_delta_20
            team_dict[team_name]['tower_delta_20_count'] = team_dict[team_name]['tower_delta_20_count'] + player_stats.tower_delta_20_count
            team_dict[team_name]['total_win'] = team_dict[team_name]['total_win'] + player_stats.win_count
            team_dict[team_name]['total_win_time'] = team_dict[team_name]['total_win_time'] + player_stats.win_time
            team_dict[team_name]['total_lost'] = team_dict[team_name]['total_lost'] + player_stats.lost_count
            team_dict[team_name]['total_lost_time'] = team_dict[team_name]['total_lost_time'] + player_stats.lost_time
        else:
            team_dict[team_name] = {
                'gold_10_total': player_stats.gold_10,
                'gold_10_count': player_stats.gold_10_count,
                'gold_20_total': player_stats.gold_20,
                'gold_20_count': player_stats.gold_20_count,
                'tower_delta_10_total': player_stats.tower_delta_10,
                'tower_delta_10_count': player_stats.tower_delta_10_count,
                'tower_delta_20_total': player_stats.tower_delta_20,
                'tower_delta_20_count': player_stats.tower_delta_20_count,
                'total_win': player_stats.win_count,
                'total_win_time': player_stats.win_time,
                'total_lost': player_stats.lost_count,
                'total_lost_time': player_stats.lost_time
            }
    value_dict = {}
    for team_name in team_dict:
        gold_10_total = team_dict[team_name]['gold_10_total']
        gold_10_count = team_dict[team_name]['gold_10_count'] if team_dict[team_name]['gold_10_count'] > 0 else 1
        gold_20_total = team_dict[team_name]['gold_20_total']
        gold_20_count = team_dict[team_name]['gold_20_count'] if team_dict[team_name]['gold_20_count'] > 0 else 1
        tower_delta_10_total = team_dict[team_name]['tower_delta_10_total']
        tower_delta_10_count = team_dict[team_name]['tower_delta_10_count'] if team_dict[team_name]['tower_delta_10_count'] > 0 else 1
        tower_delta_20_total = team_dict[team_name]['tower_delta_20_total']
        tower_delta_20_count = team_dict[team_name]['tower_delta_20_count'] if team_dict[team_name]['tower_delta_20_count'] > 0 else 1
        total_win = team_dict[team_name]['total_win'] if team_dict[team_name]['total_win'] > 0 else 1
        total_win_time = team_dict[team_name]['total_win_time']
        total_lost = team_dict[team_name]['total_lost'] if team_dict[team_name]['total_lost'] > 0 else 1
        total_lost_time = team_dict[team_name]['total_lost_time']
        avg_10 = normalize(gold_10_total / gold_10_count, min_avg_gold_10, max_avg_gold_10)
        avg_20 = normalize(gold_20_total / gold_20_count, min_avg_gold_20, max_avg_gold_20)
        avg_delta_10 = normalize(tower_delta_10_total / tower_delta_10_count, min_tower_delta_10, max_tower_delta_10)
        avg_delta_20 = normalize(tower_delta_20_total / tower_delta_20_count, min_tower_delta_20, max_tower_delta_20)
        win_rate = total_win / (total_lost + total_win)
        avg_win_time = normalize(total_win_time / total_win, min_win_time, max_win_time)
        avg_lost_time = normalize(total_lost_time / total_lost, min_lost_time, max_lost_time)
        value_dict[team_name] = avg_10 * weights[0] + avg_20 * weights[1] + avg_delta_10 * weights[2] + avg_delta_20 * weights[3] + win_rate * weights[4] + avg_win_time * weights[5] + avg_lost_time * weights[6]
        team_rankings = [k for k,v in sorted(value_dict.items(), key=lambda item: item[1])]
        value_dict = {k: v for k,v in sorted(value_dict.items(), key=lambda item: item[1])}
    # return value_dict
    return team_rankings
            

class DataView(View):
    def get(self, request):
        queryset = PlayerStats.objects.all()
        serialized = PlayerStatsSerializer(queryset, many=True)
        return JsonResponse({'data': serialized.data}, status=200)

class GlobalView(View):
    def post(self, request):
        amount = 20
        if request.body:
            data = json.loads(request.body.decode('utf-8'))
            amount = data.get('amount', 20)
        # hardcoded date incase there is no updates on new games added into database
        today = date(2023, 8, 18)
        six_months_back = today + relativedelta(months=-6)
        queryset = PlayerStats.objects.filter(start_date__range=[six_months_back, today])
        team_rankings = compute_weights(queryset)
        return JsonResponse({'data': team_rankings[:amount]}, status=200)


class GlobalAllView(View):
    def post(self, request):
        amount = 20
        if request.body:
            data = json.loads(request.body.decode('utf-8'))
            amount = data.get('amount', 20)
        queryset = PlayerStats.objects.all()
        team_rankings = compute_weights(queryset)
        return JsonResponse({'data': team_rankings[:amount]}, status=200)


class TournamentView(View):
    def post(self, request):
        tournament_id = 0
        stage = ''
        if request.body:
            data = json.loads(request.body.decode('utf-8'))
            stage = data.get('stage', '')
            tournament_id = data.get('tournament_id', 0)
        else:
            return HttpResponse('missing parameters', status=422)
        queryset = PlayerStats.objects.filter(tournament_id=tournament_id, stage_slug=stage) if stage != '' else PlayerStats.objects.filter(tournament_id=tournament_id)
        if queryset.exists():
            team_rankings = compute_weights(queryset)
            return JsonResponse({'data': team_rankings}, status=200)
        else:
            return HttpResponse('tournament_id or stage does not exists', status=400)


class TeamView(View):
    def post(self, request):
        if request.body:
            data = json.loads(request.body.decode('utf-8'))
            team_ids = data.get('team_ids', [])
        if len(team_ids) < 1:
            return HttpResponse('misisng team_ids', status=400)
        # hardcoded date incase there is no updates on new games added into database
        today = date(2023, 8, 18)
        six_months_back = today + relativedelta(months=-6)
        queryset = PlayerStats.objects.filter(start_date__range=[six_months_back, today], team_id__in=team_ids)
        if queryset.exists():
            team_rankings = compute_weights(queryset)
            return JsonResponse({'data': team_rankings}, status=200)
        else:
            return HttpResponse('no team with ids', status=400)


class TeamAllView(View):
    def post(self, request):
        if request.body:
            data = json.loads(request.body.decode('utf-8'))
            team_ids = data.get('team_ids', [])
        if len(team_ids) < 1:
            return HttpResponse('misisng team_ids', status=400)
        queryset = PlayerStats.objects.filter(team_id__in=team_ids)
        if queryset.exists():
            team_rankings = compute_weights(queryset)
            return JsonResponse({'data': team_rankings}, status=200)
        else:
            return HttpResponse('no team with ids', status=400)

