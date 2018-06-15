from django.db import models


class Goalies(models.Model):

    player = models.CharField(max_length=30, default='')
    player_id = models.CharField(max_length=7, default='')
    game_id = models.IntegerField(null=True)
    season = models.IntegerField(null=True)
    date = models.DateField(null=True)
    team = models.CharField(max_length=3, default='', null=True)
    opponent = models.CharField(max_length=3, default='', null=True)
    home = models.CharField(max_length=3, default='', null=True)
    strength = models.CharField(max_length=3, default='', null=True)
    shots_a = models.IntegerField(null=True)
    goals_a = models.IntegerField(null=True)
    fenwick_a = models.IntegerField(null=True)
    xg_a = models.FloatField(null=True)
    corsi_a = models.IntegerField(null=True)
    toi_on = models.IntegerField(null=True)
    toi_off = models.IntegerField(null=True)
    shots_a_sa = models.FloatField(null=True)
    fenwick_a_sa = models.FloatField(null=True)
    corsi_a_sa = models.FloatField(null=True)
    if_empty = models.IntegerField(null=True)
    primary_key = models.CharField(max_length=100, primary_key=True, default='')
    shooter_xg_a = models.FloatField(null=True)

    def __str__(self):
        return self.player







    
   



