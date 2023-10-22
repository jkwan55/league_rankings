from data.models import PlayerStats
all_objs = PlayerStats.objects.all().order_by('start_date')
all_missing = all_objs.filter(team_id__isnull=True)

for x in all_missing:
	filtered_players = all_objs.filter(player_id=x.player_id)
	index = filtered_players.filter(stat_id__lt = x.stat_id).count()
	prev_team_id = -1
	next_team_id = -2
	if len(filtered_players)-1 > index:
		next_team_id = filtered_players[index+1].team_id
	if index > 0:
		prev_team_id = filtered_players[index-1].team_id
	if next_team_id == prev_team_id and next_team_id and prev_team_id:
        print('found ', x.player_id, x.next_team_id)
        x.team_id = next_team_id
        x.save()