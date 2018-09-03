from django.views import generic
from .models import GamePreds
from django.http import JsonResponse
from django.db.models import Q


class IndexView(generic.ListView):
    template_name = 'game_preds/index.html'

    # Return Probabilities for that day
    def get_queryset(self):
        return []


def query_data(request):
    """
    View for Querying Data 

    :param request: GET request with query parameters

    :return: JsonResponse with info
    """
    # Query by date and team and convert to list
    query = GamePreds.objects.filter(date__range=[request.GET.get('date_filter_from'), request.GET.get('date_filter_to')])
    query = filter_team(query, request.GET.get('team'))
    query_list = list(query.values())

    # Add Season and get probs for home and away
    query_list = [add_season(game) for game in query_list]
    query_list = [get_home_away_probs(game) for game in query_list]

    return JsonResponse({'data': query_list})


def filter_team(data, team):
    """
    Filter by team selected. Must check both home and away teams!!!

    :param data: data we have at that point
    :param team: team selected (if any)

    :return: query
    """
    if team != 'All':
        return data.filter(Q(home_team=team) | Q(away_team=team))
    else:
        return data


def get_home_away_probs(game):
    """
    Get Probabilities for home and away wins based on the META classifier
    
    NOTE: Deletes extraneous probability info
    
    :param game: data for given game
    
    :return: game with both probs
    """
    game['home_probs'] = str(round(game['meta_probs'] * 100, 2)) + "%"
    game['away_probs'] = str(round((1 - game['meta_probs']) * 100, 2))  + "%"

    del game['team_probs'], game['player_probs'], game['elo_probs'], game['meta_probs']

    return game


def add_season(game):
    """
    Add Season into every game
    
    :param game: specific game
    
    :return: Data with season add in 
    """
    game['season'] = int(str(game['game_id'])[:4])

    return game
