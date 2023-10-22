from rest_framework import serializers
from .models import PlayerStats

class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = (
            'stat_id',
            'start_date',
            'tournament_id',
            'stage_slug',
            'player_id',
            'player_name',
            'gold_10',
            'gold_10_count',
            'tower_delta_10',
            'tower_delta_10_count',
            'gold_20',
            'gold_20_count',
            'tower_delta_20',
            'tower_delta_20_count',
            'win_time',
            'win_count',
            'lost_time',
            'lost_count',
            'team_id',
            'role',
            'team_name'
        )