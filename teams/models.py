from django.db import models


class Teams(models.Model):

    team = models.CharField(max_length=3, default='')
    game_id = models.IntegerField(null=True)
    season = models.IntegerField(null=True)
    date = models.DateField(null=True)
    opponent = models.CharField(max_length=3, default='', null=True)
    home = models.CharField(max_length=3, default='', null=True)
    strength = models.CharField(max_length=3, default='', null=True)
    toi = models.IntegerField(null=True)
    shots_f = models.IntegerField(null=True)
    goals_f = models.IntegerField(null=True)
    fenwick_f = models.IntegerField(null=True)
    corsi_f = models.IntegerField(null=True)
    shots_a = models.IntegerField(null=True)
    goals_a = models.IntegerField(null=True)
    fenwick_a = models.IntegerField(null=True)
    corsi_a = models.IntegerField(null=True)
    pent = models.IntegerField(null=True)
    pend = models.IntegerField(null=True)
    gives = models.IntegerField(null=True)
    takes = models.IntegerField(null=True)
    hits_f = models.IntegerField(null=True)
    hits_a = models.IntegerField(null=True)
    face_w = models.IntegerField(null=True)
    face_l = models.IntegerField(null=True)
    face_off = models.IntegerField(null=True)
    face_def = models.IntegerField(null=True)
    face_neu = models.IntegerField(null=True)
    shots_f_sa = models.FloatField(null=True)
    fenwick_f_sa = models.FloatField(null=True)
    corsi_f_sa = models.FloatField(null=True)
    shots_a_sa = models.FloatField(null=True)
    fenwick_a_sa = models.FloatField(null=True)
    corsi_a_sa = models.FloatField(null=True)
    if_empty = models.IntegerField(null=True)
    primary_key = models.CharField(max_length=100, primary_key=True, default='')

    def __str__(self):
        return self.team
