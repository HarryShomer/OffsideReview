from django.views import generic
from .models import SeasonProjs
from django.http import JsonResponse
import datetime


class IndexView(generic.ListView):
    template_name = 'season_projs/index.html'

    # Return Probabilities for that day
    def get_queryset(self):
        return []


def query_data(request):
    """
    View for Querying Data 

    :param request: GET request with query parameters

    :return: JsonResponse with info
    """
    # Date of last entry in db
    last_date = SeasonProjs.objects.latest('date').__dict__['date']

    # Query by date and team and convert to list
    query = SeasonProjs.objects.filter(date=last_date)
    query_list = list(query.values())

    # Add Season and get probs for home and away
    query_list = [get_probs(team) for team in query_list]

    return JsonResponse({'data': query_list})


def get_probs(team):
    """
    Get Probabilities for playoff stuff. 
    Round and convert to a string to get the percent sign

    :param team: data for given team

    :return: team and probs
    """
    team['points_avg'] = round(team['points_avg'], 2)
    team['points_std'] = round(team['points_std'], 2)
    team['round_1_prob'] = str(round(team['round_1_prob'] * 100, 2)) + "%"
    team['round_2_prob'] = str(round(team['round_2_prob'] * 100, 2)) + "%"
    team['round_3_prob'] = str(round(team['round_3_prob'] * 100, 2)) + "%"
    team['round_4_prob'] = str(round(team['round_4_prob'] * 100, 2)) + "%"
    team['champion_prob'] = str(round(team['champion_prob'] * 100, 2)) + "%"

    return team
