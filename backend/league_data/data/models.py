# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class PlayerStats(models.Model):
    stat_id = models.BigAutoField(unique=True, primary_key=True)
    start_date = models.DateField(blank=True, null=True)
    tournament_id = models.PositiveBigIntegerField(blank=True, null=True)
    stage_slug = models.CharField(max_length=100, blank=True, null=True)
    player_id = models.PositiveBigIntegerField(blank=True, null=True)
    player_name = models.CharField(max_length=100, blank=True, null=True)
    gold_10 = models.PositiveBigIntegerField(blank=True, null=True)
    gold_10_count = models.PositiveIntegerField(blank=True, null=True)
    tower_delta_10 = models.IntegerField(blank=True, null=True)
    tower_delta_10_count = models.IntegerField(blank=True, null=True)
    gold_20 = models.PositiveBigIntegerField(blank=True, null=True)
    gold_20_count = models.PositiveIntegerField(blank=True, null=True)
    tower_delta_20 = models.IntegerField(blank=True, null=True)
    tower_delta_20_count = models.IntegerField(blank=True, null=True)
    win_time = models.PositiveBigIntegerField(blank=True, null=True)
    win_count = models.IntegerField(blank=True, null=True)
    lost_time = models.PositiveBigIntegerField(blank=True, null=True)
    lost_count = models.IntegerField(blank=True, null=True)
    team_id = models.PositiveBigIntegerField(blank=True, null=True)
    role = models.CharField(max_length=200, blank=True, null=True)
    team_name = models.CharField(max_length=200, blank=True, null=True)


    class Meta:
        db_table = 'player_stats'

class RecordedTournaments(models.Model):
    record_id = models.BigAutoField(unique=True, primary_key=True)
    tournament_id = models.PositiveBigIntegerField(blank=True, null=True)
    tournament_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'recorded_tournaments'


class FeatureWeights(models.Model):
    weight_id = models.BigAutoField(unique=True, primary_key=True)
    weight_name = models.CharField(max_length=100, blank=True, null=True)
    weight_value = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'feature_weights'
