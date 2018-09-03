from django.db import models


class GamePreds(models.Model):
    game_id = models.IntegerField(primary_key=True)
    date = models.DateField(null=True)
    home_team = models.CharField(max_length=3, default='', null=True)
    away_team = models.CharField(max_length=3, default='', null=True)
    team_probs = models.FloatField()
    player_probs = models.FloatField()
    elo_probs = models.FloatField()
    meta_probs = models.FloatField()
