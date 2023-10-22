from data.models import PlayerStats
from django.core.management.base import BaseCommand

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
        lcs_stats = PlayerStats.objects.filter(team_id__isnull=False)
        distinct_teams = [x['team_id'] for x in lcs_stats.values('team_id').distinct()]
        
        min_avg_gold_10 = float('inf')
        max_avg_gold_10 = float('-inf')
        min_avg_gold_20 = float('inf')
        max_avg_gold_20 = float('-inf')

        min_tower_delta_10 = float('inf')
        max_tower_delta_10 = float('-inf')
        min_tower_delta_20 = float('inf')
        max_tower_delta_20 = float('-inf')

        min_total_win = float('inf')
        max_total_win = float('-inf')
        min_total_lost = float('inf')
        max_total_lost = float('-inf')
        
        min_win_time = float('inf')
        max_win_time = float('-inf')
        min_lost_time = float('inf')
        max_lost_time = float('-inf')

        for team_id in distinct_teams:
            team_stats_all = lcs_stats.filter(team_id=team_id)
            distinct_tournaments = [x['tournament_id'] for x in team_stats_all.values('tournament_id').distinct()]
            for x in distinct_tournaments:
                team_stats = team_stats_all.filter(tournament_id=x)
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
                
                avg_10 = gold_10_total / (gold_10_count if gold_10_count != 0 else 1)
                avg_20 = gold_20_total / (gold_20_count if gold_20_count != 0 else 1)
                avg_delta_10 = tower_delta_10_total / (tower_delta_10_count if tower_delta_10_count != 0 else 1)
                avg_delta_20 = tower_delta_20_total / (tower_delta_20_count if tower_delta_20_count != 0 else 1)
                win_rate = total_win / (total_lost + total_win)
                avg_win_time = total_win_time / (total_win if total_win != 0 else 1)
                avg_lost_time = total_lost_time / (total_lost if total_lost != 0 else 1)

                min_avg_gold_10 = min(min_avg_gold_10, avg_10)
                max_avg_gold_10 = max(max_avg_gold_10, avg_10)
                min_avg_gold_20 = min(min_avg_gold_20, avg_20)
                max_avg_gold_20 = max(max_avg_gold_20, avg_20)

                min_tower_delta_10 = min(min_tower_delta_10, avg_delta_10)
                max_tower_delta_10 = max(max_tower_delta_10, avg_delta_10)
                min_tower_delta_20 = min(min_tower_delta_20, avg_delta_20)
                max_tower_delta_20 = max(max_tower_delta_20, avg_delta_20)

                min_total_win = min(min_total_win, total_win)
                max_total_win = max(max_total_win, total_win)
                min_total_lost = min(min_total_lost, total_lost)
                max_total_lost = max(max_total_lost, total_lost)
                
                min_win_time = min(min_win_time, avg_win_time) if avg_win_time != 0 else min_win_time
                max_win_time = max(max_win_time, avg_win_time)
                min_lost_time = min(min_lost_time, avg_lost_time) if avg_lost_time != 0 else min_lost_time
                max_lost_time = max(max_lost_time, avg_lost_time)

        print('min_avg_gold_10', min_avg_gold_10)
        print('max_avg_gold_10', max_avg_gold_10)
        print('min_avg_gold_20', min_avg_gold_20)
        print('max_avg_gold_20', max_avg_gold_20)

        print('min_tower_delta_10', min_tower_delta_10)
        print('max_tower_delta_10', max_tower_delta_10)
        print('min_tower_delta_20', min_tower_delta_20)
        print('max_tower_delta_20', max_tower_delta_20)

        print('min_total_win', min_total_win)
        print('max_total_win', max_total_win)
        print('min_total_lost', min_total_lost)
        print('max_total_lost', max_total_lost)

        print('min_win_time', min_win_time)
        print('max_win_time', max_win_time)
        print('min_lost_time', min_lost_time)
        print('max_lost_time', max_lost_time)

