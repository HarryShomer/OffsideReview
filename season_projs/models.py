from django.db import models


class SeasonProjs(models.Model):
    """
    Model Fields
    """
    # team_date -> ex: "NYR_2017-10-08"
    primary_key = models.CharField(max_length=15, primary_key=True)

    team = models.CharField(max_length=3, default='')
    date = models.DateField()

    points_avg = models.FloatField()
    points_std = models.FloatField()

    # Probability of *getting* there.
    # So 'round_3_prob' is the probability of making it to the third round or winning the 2nd round
    round_1_prob = models.FloatField()
    round_2_prob = models.FloatField()
    round_3_prob = models.FloatField()
    round_4_prob = models.FloatField()
    champion_prob = models.FloatField()

