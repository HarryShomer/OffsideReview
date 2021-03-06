from django.views import generic
from .models import Goalies
from django.http import JsonResponse
from django.db.models import Sum, Count
from helpers.query_helpers import *


class IndexView(generic.ListView):
    template_name = 'goalies/index.html'

    def get_queryset(self):
        return []


def get_search_list(request):
    """
    View for getting goalie search list when page loads
    
    :param request: Nothing really 
    
    :return: JsonResponse with goalies
    """
    players = list(Goalies.objects.values_list('player', flat=True))
    players = list(set(players))
    players.sort()
    players.insert(0, '')

    return JsonResponse(players, safe=False)


def query_data(request):
    """
    View for Querying Data 
    
    :param request: GET request with query parameters
    
    :return: JsonResponse with info
    """
    strength = request.GET.get('strength')
    split_by = request.GET.get('split_by')
    team = request.GET.get('team')
    venue = request.GET.get('venue')
    player_search = request.GET.get('search')
    season_type = request.GET.get('season_type')
    date_filter_from = request.GET.get('date_filter_from')
    date_filter_to = request.GET.get('date_filter_to')
    adjustment = request.GET.get('adjustment')
    toi = request.GET.get('toi')

    query = Goalies.objects.filter(date__range=[date_filter_from, date_filter_to])
    query = filter_players(query, player_search)
    query = filter_team(query, team)
    query = filter_strength(query, strength)
    query = filter_season_type(query, season_type)
    query = filter_venue(query, venue)

    # Season or Game
    if split_by == 'Season':
        players = filter_by_season(query, toi, adjustment)
    elif split_by == 'Cumulative':
        players = filter_by_cumulative(query, toi, adjustment)
    elif split_by == 'Game':
        players = filter_by_game(query, toi, adjustment)

    return JsonResponse({'data': [calculate_statistics(player, strength, adjustment) for player in players]})


def filter_by_cumulative(data, toi, adjustment):
    """
    Filter by season (also filter by toi here)
    
    :param data: data we have at that point 
    :param toi: toi filter
    :param adjustment: ex: "Score Adjusted"
    
    :return: list (of dicts) who match criteria
    """
    cols = ['player', 'games', 'team', 'games', 'goals_a', 'shots_a', 'fenwick_a', 'xg_a', 'corsi_a', 'toi_on',
            'sh_xg_a']

    if adjustment == 'Score Adjusted':
        # These columns are to hold non adjusted numbers for percentages when using score adjusted numbers
        cols = cols + ['shots_a_raw', 'fenwick_a_raw']

        data = data.values('player', 'player_id', 'team')\
            .annotate(games=Count('game_id', distinct=True), goals_a=Sum('goals_a'), shots_a_raw=Sum('shots_a'),
                      fenwick_a_raw=Sum('fenwick_a'), shots_a=Sum('shots_a_sa'), fenwick_a=Sum('fenwick_a_sa'),
                      corsi_a=Sum('corsi_a_sa'), xg_a=Sum('xg_a'), toi_on=Sum('toi_on'), sh_xg_a=Sum('shooter_xg_a'))
    else:
        data = data.values('player', 'player_id', 'team') \
            .annotate(games=Count('game_id', distinct=True), goals_a=Sum('goals_a'), shots_a=Sum('shots_a'),
                      fenwick_a=Sum('fenwick_a'), corsi_a=Sum('corsi_a'), xg_a=Sum('xg_a'), toi_on=Sum('toi_on'),
                      sh_xg_a=Sum('shooter_xg_a'))

    data = filter_toi(data, toi, False)

    return list(data.values(*cols))


def filter_by_season(data, toi, adjustment):
    """
    Filter by season (also filter by toi here)
    
    :param data: data we have at that point 
    :param toi: toi filter
    :param adjustment: ex: "Score Adjusted"
    
    :return: list (of dicts) who match criteria
    """
    cols = ['player', 'games', 'team', 'season', 'games', 'shots_a', 'goals_a', 'fenwick_a', 'xg_a', 'corsi_a',
            'toi_on', 'sh_xg_a']

    if adjustment == 'Score Adjusted':
        # These columns are to hold non adjusted numbers for percentages when using score adjusted numbers
        cols = cols + ['shots_a_raw', 'fenwick_a_raw']

        data = data.values('player', 'player_id', 'season', 'team') \
            .annotate(games=Count('game_id', distinct=True), goals_a=Sum('goals_a'), shots_a_raw=Sum('shots_a'),
                      fenwick_a_raw=Sum('fenwick_a'), shots_a=Sum('shots_a_sa'), fenwick_a=Sum('fenwick_a_sa'),
                      corsi_a=Sum('corsi_a_sa'), xg_a=Sum('xg_a'), toi_on=Sum('toi_on'), sh_xg_a=Sum('shooter_xg_a'))
    else:
        data = data.values('player', 'player_id', 'season', 'team')\
            .annotate(games=Count('game_id', distinct=True), shots_a=Sum('shots_a'), goals_a=Sum('goals_a'),
                      fenwick_a=Sum('fenwick_a'), corsi_a=Sum('corsi_a'), xg_a=Sum('xg_a'), toi_on=Sum('toi_on'),
                      sh_xg_a=Sum('shooter_xg_a'))

    data = filter_toi(data, toi, False)

    return list(data.values(*cols))


def filter_by_game(data, toi, adjustment):
    """
    Filter by game (also filter by toi here)
    
    :param data: data we have at that point 
    :param toi: toi filter
    :param adjustment: ex: "Score Adjusted"
    
    :return: list (of dicts) who match criteria 
    """
    cols = ['player', 'game_id', 'team', 'season', 'date', 'opponent', 'home', 'shots_a', 'goals_a', 'fenwick_a',
            'xg_a', 'corsi_a', 'toi_on', 'sh_xg_a']

    if adjustment == 'Score Adjusted':
        # These columns are to hold non adjusted numbers for percentages when using score adjusted numbers
        cols = cols + ['shots_a_raw', 'fenwick_a_raw']

        data = data.values('player', 'player_id', 'season', 'game_id', 'team', 'date', 'opponent', 'home') \
            .annotate(goals_a=Sum('goals_a'), shots_a_raw=Sum('shots_a'), fenwick_a_raw=Sum('fenwick_a'),
                      shots_a=Sum('shots_a_sa'), fenwick_a=Sum('fenwick_a_sa'), corsi_a=Sum('corsi_a_sa'),
                      xg_a=Sum('xg_a'), toi_on=Sum('toi_on'), sh_xg_a=Sum('shooter_xg_a'))
    else:
        data = data.values('player', 'player_id', 'season', 'game_id',  'team', 'date', 'opponent', 'home') \
            .annotate(goals_a=Sum('goals_a'), shots_a=Sum('shots_a'), fenwick_a=Sum('fenwick_a'),
                      corsi_a=Sum('corsi_a'), xg_a=Sum('xg_a'), toi_on=Sum('toi_on'), sh_xg_a=Sum('shooter_xg_a'))

    data = filter_toi(data, toi, False)

    return list(data.values(*cols))


def calculate_statistics(player, strength, adjustment):
    """
    Calculate statistics for goalies 
    Note: I don't use score adjusted for goals_a, Sv%, and Miss%
    
    :param player: player -> with dict of raw numbers
    :param strength -> strength specified in search
    :param adjustment
    
    :return: Calculated stats added to list
    """
    player['toi_on'] = format(player['toi_on'] / 60, '.2f')  # Convert to minutes
    player['strength'] = strength

    # TODO: Need to figure out a cleaner way than this work around
    # If it's in there we know it's score adjusted ... so we use those with pct at end
    if 'shots_a_raw' in list(player.keys()):
        player['Sv%'] = get_pct(player['shots_a_raw']-player['goals_a'], player['shots_a_raw'])
        player['xFSv%'] = get_pct(player['fenwick_a_raw'] - player['xg_a'], player['fenwick_a_raw'])
        player['FSv%'] = get_pct(player['fenwick_a_raw'] - player['goals_a'], player['fenwick_a_raw'])
        player['Miss%'] = get_pct(player['fenwick_a_raw'] - player['shots_a_raw'], player['fenwick_a_raw'])
    else:
        player['Sv%'] = get_pct(player['shots_a'] - player['goals_a'], player['shots_a'])
        player['xFSv%'] = get_pct(player['fenwick_a'] - player['xg_a'], player['fenwick_a'])
        player['FSv%'] = get_pct(player['fenwick_a'] - player['goals_a'], player['fenwick_a'])
        player['Miss%'] = get_pct(player['fenwick_a'] - player['shots_a'], player['fenwick_a'])

    # Per 60's
    player['shots_a_60'] = get_per_60(player['toi_on'], player['shots_a'])
    player['goals_a_60'] = get_per_60(player['toi_on'], player['goals_a'])
    player['fenwick_a_60'] = get_per_60(player['toi_on'], player['fenwick_a'])
    player['corsi_a_60'] = get_per_60(player['toi_on'], player['corsi_a'])
    player['xg_a_60'] = get_per_60(player['toi_on'], player['xg_a'])

    # Adjusted Sv%
    player['adj_sv'] = get_adj_sv(player['FSv%'], player['xFSv%'])

    # Too many decimals
    player['xg_a'] = round(player['xg_a'], 2)
    player['sh_xg_a'] = round(player['sh_xg_a'], 2)

    if adjustment == 'Score Adjusted':
        player['shots_a'] = format(player['shots_a'], '.2f')
        player['fenwick_a'] = format(player['fenwick_a'], '.2f')
        player['corsi_a'] = format(player['corsi_a'], '.2f')

    return player


def get_adj_sv(sv, exp_sv):
    """
    Get Adjusted Sv% -> Actual - Expected
    
    :param sv: Actual sv
    :param exp_sv: Expected Sv%
    
    :return: Adjusted Sv%
    """
    try:
        return format(float(sv) - float(exp_sv), '.2f')
    except ValueError:
        return ''
