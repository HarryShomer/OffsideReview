from django.views import generic
from .models import Teams
from django.http import JsonResponse
from django.db.models import Sum, Count
from helpers.query_helpers import *


class IndexView(generic.ListView):
    template_name = 'teams/index.html'

    def get_queryset(self):
        return []


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
    season_type = request.GET.get('season_type')
    date_filter_from = request.GET.get('date_filter_from')
    date_filter_to = request.GET.get('date_filter_to')
    adjustment = request.GET.get('adjustment')
    toi = request.GET.get('toi')

    query = Teams.objects.filter(date__range=[date_filter_from, date_filter_to])
    query = filter_season_type(query, season_type)
    query = filter_strength(query, strength)
    query = filter_venue(query, venue)
    query = filter_team(query, team)

    # Season or Game
    if split_by == 'Season':
        teams = filter_by_season(query, toi, adjustment)
    elif split_by == 'Cumulative':
        teams = filter_by_cumulative(query, toi, adjustment)
    else:
        teams = filter_by_game(query, toi, adjustment)

    return JsonResponse({'data': [calculate_statistics(team, strength, adjustment) for team in teams]})


def filter_by_cumulative(data, toi, adjustment):
    """
    Filter by season (also filter by toi here)
    
    :param data: data we have at that point 
    :param toi: toi filter
    :param adjustment: ex: "Score Adjusted"
    
    :return: list (of dicts) who match criteria
    """
    cols = ['team', 'games', 'goals_a', 'goals_f', 'shots_a', 'shots_f', 'fenwick_a', 'fenwick_f', 'corsi_a', 'corsi_f',
            'xg_a', 'xg_f', 'pent', 'pend', 'hits_f', 'hits_a', 'gives', 'takes', 'face_l', 'face_w', 'face_off',
            'face_def', 'face_neu', 'toi', "sh_xg_f", "sh_xg_a"]

    if adjustment == 'Score Adjusted':
        # These columns are to hold non adjusted numbers for percentages when using score adjusted numbers
        cols = cols + ['shots_f_raw', 'shots_a_raw', 'fenwick_f_raw', 'fenwick_a_raw']

        data = data.values('team') \
            .annotate(games=Count('game_id', distinct=True), goals_a=Sum('goals_a'), shots_a_raw=Sum('shots_a'),
                      fenwick_a_raw=Sum('fenwick_a'), shots_f_raw=Sum('shots_f'), fenwick_f_raw=Sum('fenwick_f'),
                      shots_a=Sum('shots_a_sa'), fenwick_a=Sum('fenwick_a_sa'), corsi_a=Sum('corsi_a_sa'),
                      goals_f=Sum('goals_f'), toi=Sum('toi'),  shots_f=Sum('shots_f_sa'), fenwick_f=Sum('fenwick_f_sa'),
                      corsi_f=Sum('corsi_f_sa'), pent=Sum('pent'), pend=Sum('pend'), gives=Sum('gives'), takes=Sum('takes'),
                      hits_f=Sum('hits_f'), hits_a=Sum('hits_a'), face_l=Sum('face_l'), face_w=Sum('face_w'),
                      face_off=Sum('face_off'), face_def=Sum('face_def'), face_neu=Sum('face_neu'), xg_a=Sum('xg_a'),
                      xg_f=Sum('xg_f'), sh_xg_f=Sum("shooter_xg_f"), sh_xg_a=Sum("shooter_xg_a"))
    else:
        data = data.values('team') \
            .annotate(games=Count('game_id', distinct=True), goals_a=Sum('goals_a'), shots_a=Sum('shots_a'),
                      fenwick_a=Sum('fenwick_a'), corsi_a=Sum('corsi_a'), goals_f=Sum('goals_f'), toi=Sum('toi'),
                      shots_f=Sum('shots_f'), fenwick_f=Sum('fenwick_f'), corsi_f=Sum('corsi_f'), pent=Sum('pent'),
                      pend=Sum('pend'), gives=Sum('gives'), takes=Sum('takes'), hits_f=Sum('hits_f'),
                      hits_a=Sum('hits_a'), face_l=Sum('face_l'), face_w=Sum('face_w'), face_off=Sum('face_off'),
                      face_def=Sum('face_def'), face_neu=Sum('face_neu'), xg_a=Sum('xg_a'), xg_f=Sum('xg_f'),
                      sh_xg_f=Sum("shooter_xg_f"), sh_xg_a=Sum("shooter_xg_a"))

    data = filter_toi(data, toi, True)

    return list(data.values(*cols))


def filter_by_season(data, toi, adjustment):
    """
    Filter by season (also filter by toi here)
    
    :param data: data we have at that point 
    :param toi: toi filter
    :param adjustment: ex: "Score Adjusted"
    
    :return: list (of dicts) who match criteria
    """
    cols = ['team', 'season', 'games', 'goals_a', 'goals_f', 'shots_a', 'shots_f', 'fenwick_a', 'fenwick_f', 'corsi_a',
            'corsi_f', 'xg_a', 'xg_f', 'pent', 'pend', 'hits_f', 'hits_a', 'gives', 'takes', 'face_l', 'face_w',
            'face_off', 'face_def', 'face_neu', 'toi', "sh_xg_f", "sh_xg_a"]

    if adjustment == 'Score Adjusted':
        # These columns are to hold non adjusted numbers for percentages when using score adjusted numbers
        cols = cols + ['shots_f_raw', 'shots_a_raw', 'fenwick_f_raw', 'fenwick_a_raw']

        data = data.values('team', 'season') \
            .annotate(games=Count('game_id', distinct=True), goals_a=Sum('goals_a'), shots_a_raw=Sum('shots_a'),
                      fenwick_a_raw=Sum('fenwick_a'), shots_f_raw=Sum('shots_f'), fenwick_f_raw=Sum('fenwick_f'),
                      shots_a=Sum('shots_a_sa'), fenwick_a=Sum('fenwick_a_sa'), corsi_a=Sum('corsi_a_sa'),
                      goals_f=Sum('goals_f'), toi=Sum('toi'), shots_f=Sum('shots_f_sa'), fenwick_f=Sum('fenwick_f_sa'),
                      corsi_f=Sum('corsi_f_sa'), pent=Sum('pent'), pend=Sum('pend'), gives=Sum('gives'), takes=Sum('takes'),
                      hits_f=Sum('hits_f'), hits_a=Sum('hits_a'), face_l=Sum('face_l'), face_w=Sum('face_w'),
                      face_off=Sum('face_off'), face_def=Sum('face_def'), face_neu=Sum('face_neu'), xg_a=Sum('xg_a'),
                      xg_f=Sum('xg_f'), sh_xg_f=Sum("shooter_xg_f"), sh_xg_a=Sum("shooter_xg_a"))
    else:
        data = data.values('team', 'season') \
            .annotate(games=Count('game_id', distinct=True), goals_a=Sum('goals_a'), shots_a=Sum('shots_a'),
                      fenwick_a=Sum('fenwick_a'), corsi_a=Sum('corsi_a'), goals_f=Sum('goals_f'), toi=Sum('toi'),
                      shots_f=Sum('shots_f'), fenwick_f=Sum('fenwick_f'), corsi_f=Sum('corsi_f'), pent=Sum('pent'),
                      pend=Sum('pend'), gives=Sum('gives'), takes=Sum('takes'), hits_f=Sum('hits_f'),
                      hits_a=Sum('hits_a'), face_l=Sum('face_l'), face_w=Sum('face_w'), face_off=Sum('face_off'),
                      face_def=Sum('face_def'), face_neu=Sum('face_neu'), xg_a=Sum('xg_a'), xg_f=Sum('xg_f'),
                      sh_xg_f=Sum("shooter_xg_f"), sh_xg_a=Sum("shooter_xg_a"))

    data = filter_toi(data, toi, True)

    return list(data.values(*cols))


def filter_by_game(data, toi, adjustment):
    """
    Filter by game (also filter by toi here)
    
    :param data: data we have at that point 
    :param toi: toi filter
    :param adjustment: ex: "Score Adjusted"
    
    :return: list (of dicts) who match criteria 
    """
    cols = ['team', 'season', 'game_id', 'date', 'opponent', 'home', 'goals_a', 'goals_f', 'shots_a', 'shots_f',
            'fenwick_a', 'fenwick_f', 'corsi_a', 'corsi_f', 'xg_a', 'xg_f', 'pent', 'pend', 'hits_f', 'hits_a',
            'gives', 'takes', 'face_l', 'face_w', 'face_off', 'face_def', 'face_neu', 'toi', "sh_xg_f", "sh_xg_a"]

    if adjustment == 'Score Adjusted':
        # These columns are to hold non adjusted numbers for percentages when using score adjusted numbers
        cols = cols + ['shots_f_raw', 'shots_a_raw', 'fenwick_f_raw', 'fenwick_a_raw']

        data = data.values('team', 'season', 'game_id', 'date', 'opponent', 'home') \
            .annotate(goals_a=Sum('goals_a'), shots_a_raw=Sum('shots_a'), fenwick_a_raw=Sum('fenwick_a'),
                      shots_f_raw=Sum('shots_f'), fenwick_f_raw=Sum('fenwick_f'), shots_a=Sum('shots_a_sa'),
                      fenwick_a=Sum('fenwick_a_sa'), corsi_a=Sum('corsi_a_sa'), goals_f=Sum('goals_f'), toi=Sum('toi'),
                      shots_f=Sum('shots_f_sa'), fenwick_f=Sum('fenwick_f_sa'), corsi_f=Sum('corsi_f_sa'),
                      pent=Sum('pent'), pend=Sum('pend'), gives=Sum('gives'), takes=Sum('takes'), hits_f=Sum('hits_f'),
                      hits_a=Sum('hits_a'), face_l=Sum('face_l'), face_w=Sum('face_w'), face_off=Sum('face_off'),
                      face_def=Sum('face_def'), face_neu=Sum('face_neu'), xg_a=Sum('xg_a'), xg_f=Sum('xg_f'),
                      sh_xg_f=Sum("shooter_xg_f"), sh_xg_a=Sum("shooter_xg_a"))
    else:
        data = data.values('team', 'season', 'game_id', 'date', 'opponent', 'home') \
            .annotate(goals_a=Sum('goals_a'), shots_a=Sum('shots_a'), fenwick_a=Sum('fenwick_a'), corsi_a=Sum('corsi_a'),
                      goals_f=Sum('goals_f'), toi=Sum('toi'), shots_f=Sum('shots_f'), fenwick_f=Sum('fenwick_f'),
                      corsi_f=Sum('corsi_f'), pent=Sum('pent'), pend=Sum('pend'), gives=Sum('gives'), takes=Sum('takes'),
                      hits_f=Sum('hits_f'), hits_a=Sum('hits_a'), face_l=Sum('face_l'), face_w=Sum('face_w'),
                      face_off=Sum('face_off'), face_def=Sum('face_def'), face_neu=Sum('face_neu'),
                      xg_a=Sum('xg_a'), xg_f=Sum('xg_f'), sh_xg_f=Sum("shooter_xg_f"), sh_xg_a=Sum("shooter_xg_a"))

    data = filter_toi(data, toi, True)

    return list(data.values(*cols))


def calculate_statistics(team, strength, adjustment):
    """
    Calculate statistics for team
    Note: Anything involving goals isn't score adjusted
    
    :param team: team -> with dict of raw numbers
    :param strength -> strength specified in search
    :param adjustment -> ...
    
    :return: Calculated stats added to list
    """
    team['toi'] = format(team['toi'] / 60, '.2f')  # Convert to minutes
    team['strength'] = strength

    # Weighted Shots
    team['wsh_f'] = team['goals_f'] + .2 * (team['corsi_f'] - team['goals_f'])
    team['wsh_a'] = team['goals_a'] + .2 * (team['corsi_a'] - team['goals_a'])

    if 'shots_a_raw' in list(team.keys()):
        team['Sv%'] = get_pct(team['shots_a_raw'] - team['goals_a'], team['shots_a_raw'])
        team['Sh%'] = get_pct(team['goals_f'], team['shots_f_raw'])
        team['fSh%'] = get_pct(team['goals_f'], team['fenwick_f_raw'])
        team['xfSh%'] = get_pct(team['xg_f'], team['fenwick_f_raw'])
        team['FSv%'] = get_pct(team['fenwick_a_raw'] - team['goals_a'], team['fenwick_a_raw'])
        team['xFSv%'] = get_pct(team['fenwick_a_raw'] - team['xg_a'], team['fenwick_a_raw'])
        team['Miss%'] = get_pct(team['fenwick_a_raw'] - team['shots_a_raw'], team['fenwick_a_raw'])
    else:
        team['Sv%'] = get_pct(team['shots_a']-team['goals_a'], team['shots_a'])
        team['Sh%'] = get_pct(team['goals_f'], team['shots_f'])
        team['fSh%'] = get_pct(team['goals_f'], team['fenwick_f'])
        team['xfSh%'] = get_pct(team['xg_f'], team['fenwick_f'])
        team['FSv%'] = get_pct(team['fenwick_a'] - team['goals_a'], team['fenwick_a'])
        team['xFSv%'] = get_pct(team['fenwick_a'] - team['xg_a'], team['fenwick_a'])
        team['Miss%'] = get_pct(team['fenwick_a'] - team['shots_a'], team['fenwick_a'])

    team['GF%'] = get_pct(team['goals_f'], team['goals_a'] + team['goals_f'])
    team['FF%'] = get_pct(team['fenwick_f'], team['fenwick_a'] + team['fenwick_f'])
    team['CF%'] = get_pct(team['corsi_f'], team['corsi_a'] + team['corsi_f'])
    team['xGF%'] = get_pct(team['xg_f'], team['xg_a'] + team['xg_f'])
    team['wshF%'] = get_pct(team['wsh_f'], team['wsh_a'] + team['wsh_f'])

    team['shots_f_60'] = get_per_60(team['toi'], team['shots_f'])
    team['goals_f_60'] = get_per_60(team['toi'], team['goals_f'])
    team['fenwick_f_60'] = get_per_60(team['toi'], team['fenwick_f'])
    team['corsi_f_60'] = get_per_60(team['toi'], team['corsi_f'])
    team['xg_f_60'] = get_per_60(team['toi'], team['xg_f'])
    team['wsh_f_60'] = get_per_60(team['toi'], team['wsh_f'])

    team['shots_a_60'] = get_per_60(team['toi'], team['shots_a'])
    team['goals_a_60'] = get_per_60(team['toi'], team['goals_a'])
    team['fenwick_a_60'] = get_per_60(team['toi'], team['fenwick_a'])
    team['corsi_a_60'] = get_per_60(team['toi'], team['corsi_a'])
    team['xg_a_60'] = get_per_60(team['toi'], team['xg_a'])
    team['wsh_a_60'] = get_per_60(team['toi'], team['wsh_a'])

    # Decimal places...
    if adjustment == 'Score Adjusted':
        team['shots_f'] = format(team['shots_f'], '.2f')
        team['fenwick_f'] = format(team['fenwick_f'], '.2f')
        team['corsi_f'] = format(team['corsi_f'], '.2f')
        team['shots_a'] = format(team['shots_a'], '.2f')
        team['fenwick_a'] = format(team['fenwick_a'], '.2f')
        team['corsi_a'] = format(team['corsi_a'], '.2f')

    team['xg_f'] = format(team['xg_f'], '.2f')
    team['xg_a'] = format(team['xg_a'], '.2f')

    # Delete for now.....
    del team['wsh_f'], team['wsh_a'], team['sh_xg_f'], team['sh_xg_a']

    return team




