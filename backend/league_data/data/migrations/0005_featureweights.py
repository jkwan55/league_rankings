# Generated by Django 4.2.5 on 2023-10-13 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_playerstats_team_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureWeights',
            fields=[
                ('weight_id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('weight_name', models.CharField(blank=True, max_length=100, null=True)),
                ('weight_value', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'db_table': 'feature_weights',
            },
        ),
    ]