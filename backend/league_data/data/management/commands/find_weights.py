from data.models import PlayerStats
from django.core.management.base import BaseCommand
import shap
import xgboost as xgb
from sklearn.datasets import load_iris
from sklearn.linear_model import LinearRegression
import pandas as pd


class Command(BaseCommand):
    help = "Grab tournaments and save into db"

#     stat_id = models.BigAutoField(unique=True, primary_key=True)
#     start_date = models.DateField(blank=True, null=True)
#     tournament_id = models.PositiveBigIntegerField(blank=True, null=True)
#     stage_slug = models.CharField(max_length=100, blank=True, null=True)
#     player_id = models.PositiveBigIntegerField(blank=True, null=True)
#     player_name = models.CharField(max_length=100, blank=True, null=True)
#     gold_10 = models.PositiveBigIntegerField(blank=True, null=True)
#     gold_10_count = models.PositiveIntegerField(blank=True, null=True)
#     tower_delta_10 = models.IntegerField(blank=True, null=True)
#     tower_delta_10_count = models.IntegerField(blank=True, null=True)
#     gold_20 = models.PositiveBigIntegerField(blank=True, null=True)
#     gold_20_count = models.PositiveIntegerField(blank=True, null=True)
#     tower_delta_20 = models.IntegerField(blank=True, null=True)
#     tower_delta_20_count = models.IntegerField(blank=True, null=True)
#     win_time = models.PositiveBigIntegerField(blank=True, null=True)
#     win_count = models.IntegerField(blank=True, null=True)
#     lost_time = models.PositiveBigIntegerField(blank=True, null=True)
#     lost_count = models.IntegerField(blank=True, null=True)
#     team_id = models.PositiveBigIntegerField(blank=True, null=True)
#     role = models.CharField(max_length=200, blank=True, null=True)
#     team_name = models.CharField(max_length=200, blank=True, null=True)


    def handle(self, *args, **options):
        
        def normalize(target, min_val, max_val):
            return ( target - min_val ) / ( max_val - min_val )

        # lcs_stats = PlayerStats.objects.filter(tournament_id=108206581962155974, stage_slug='regular_season')
        lcs_stats = PlayerStats.objects.filter(tournament_id=108206581962155974, stage_slug='playoffs')
        distinct_teams = [x['team_id'] for x in lcs_stats.values('team_id').distinct()]

        # grab min and max from find_max_min, hard code for now, running out of time
        min_avg_gold_10 = 2068.6666666666665
        max_avg_gold_10 = 4515.9
        min_avg_gold_20 = 4281.222222222223
        max_avg_gold_20 = 9236.6
        min_tower_delta_10 = -0.5
        max_tower_delta_10 = 1.0
        min_tower_delta_20 = -5.5
        max_tower_delta_20 = 7.0
        min_total_win = 0
        max_total_win = 376
        min_total_lost = 0
        max_total_lost = 323
        min_win_time = 1166432.0
        max_win_time = 3423385.0
        min_lost_time = 1260949.0
        max_lost_time = 2733361.0
        
        shap_features = {
            'AVG_GOLD_10_WEIGHT': [],
            'AVG_GOLD_20_WEIGHT': [],
            'AVG_TOWER_DELTA_10_WEIGHT': [],
            'AVG_TOWER_DELTA_20_WEIGHT': [],
            'WIN_RATE_WEIGHT': [],
            'AVG_WIN_TIME_WEIGHT': [],
            'AVG_LOST_TIME_WEIGHT': []
        }

        shap_target = []

        weight1 = 60.850482067668835
        weight2 = -81.86179372351509
        weight3 = 22.915557140713318
        weight4 = 25.515510378538025
        weight5 = -9.376862747866605
        weight6 = -4.006092027320668
        weight7 = 2.1338514352977596

        result_dict = {}

        for team_id in distinct_teams:
            team_stats = lcs_stats.filter(team_id=team_id)
            gold_10_total = 0
            gold_10_count = 0
            gold_20_total = 0
            gold_20_count = 0
            
            tower_delta_10_total = 0
            tower_delta_10_count = 0
            tower_delta_20_total = 0
            tower_delta_20_count = 0

            total_win = 0
            total_win_time = 0
            total_lost = 0
            total_lost_time = 0
            win_rate = 0
            team_name = team_stats[0].team_name
            
            for player_stats in team_stats:
                if not team_name and player_stats.team_name:
                    team_name = player_stats.team_name
                gold_10_total += player_stats.gold_10
                gold_10_count += player_stats.gold_10_count
                gold_20_total += player_stats.gold_20
                gold_20_count += player_stats.gold_20_count

                tower_delta_10_total += player_stats.tower_delta_10
                tower_delta_10_count += player_stats.tower_delta_10_count
                tower_delta_20_total += player_stats.tower_delta_20
                tower_delta_20_count += player_stats.tower_delta_20_count

                total_win += player_stats.win_count
                total_win_time += player_stats.win_time
                total_lost += player_stats.lost_count
                total_lost_time += player_stats.lost_time
            
            avg_10 = normalize(gold_10_total / gold_10_count, min_avg_gold_10, max_avg_gold_10)
            avg_20 = normalize(gold_20_total / gold_20_count, min_avg_gold_20, max_avg_gold_20)
            avg_delta_10 = normalize(tower_delta_10_total / tower_delta_10_count, min_tower_delta_10, max_tower_delta_10)
            avg_delta_20 = normalize(tower_delta_20_total / tower_delta_20_count, min_tower_delta_20, max_tower_delta_20)
            win_rate = total_win / (total_lost + total_win)
            avg_win_time = normalize(total_win_time / total_win, min_win_time, max_win_time)
            avg_lost_time = normalize(total_lost_time / total_lost, min_lost_time, max_lost_time)
            norm_total_win = normalize(total_win, min_total_win, max_total_win)
            norm_total_lost = normalize(total_lost, min_total_lost, max_total_lost)
            
            # avg_10 = gold_10_total / gold_10_count
            # avg_20 = gold_20_total / gold_20_count
            # avg_delta_10 = tower_delta_10_total / tower_delta_10_count
            # avg_delta_20 = tower_delta_20_total / tower_delta_20_count
            # win_rate = total_win / (total_lost + total_win)
            # avg_win_time = total_win_time / total_win
            # avg_lost_time = total_lost_time / total_lost
            # norm_total_win = total_win
            # norm_total_lost = total_lost
            shap_features['AVG_GOLD_10_WEIGHT'].append(avg_10) # 1
            shap_features['AVG_GOLD_20_WEIGHT'].append(avg_20) # 2
            shap_features['AVG_TOWER_DELTA_10_WEIGHT'].append(avg_delta_10) # 3
            shap_features['AVG_TOWER_DELTA_20_WEIGHT'].append(avg_delta_20) # 4
            shap_features['WIN_RATE_WEIGHT'].append(win_rate) # 5
            shap_features['AVG_WIN_TIME_WEIGHT'].append(avg_win_time) # 6
            shap_features['AVG_LOST_TIME_WEIGHT'].append(avg_lost_time) # 7
            result_dict[team_name] = avg_10 * weight1 + avg_20 * weight2 + avg_delta_10 * weight3 + avg_delta_20 * weight4 + win_rate * weight5 + avg_win_time * weight6 + \
                avg_lost_time * weight7
        print(result_dict)
        # ranking_target = [5, 2, 4, 10, 6, 8, 9, 3, 7, 1] #regular
        ranking_target = [1, 5, 4, 7, 3, 2, 6] #playoffs
        # print(shap_target)
        X = pd.DataFrame(shap_features)
        y = ranking_target
        model = LinearRegression()
        model.fit(X, y)
        feature_weights = model.coef_
        for x in feature_weights:
            print(x)
