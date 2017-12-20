from django.views import generic
from .models import Teams
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.db.models import F


class IndexView(generic.ListView):
    template_name = 'teams/index.html'

    # Do I need this?
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

    teams = [calculate_statistics(team, strength, adjustment) for team in teams]

    response = {'data': teams}

    return JsonResponse(response)


def filter_strength(data, strength):
    """
    Filter by given strength
    :param data: data we have at that point
    :param strength: given strength
    :return: query 
    """
    # Don't do anything for All Situations
    if strength != 'All Situations':
        # If it's has a 6 they obviously want empty net stuff otherwise don't bother
        if '6' in strength:
            return data.filter(strength=strength)
        else:
            return data.filter(strength=strength).filter(if_empty=0)
    else:
        return data.exclude(strength='0x0')


def filter_team(data, team):
    """
    Filter by team selected
    :param data: data we have at that point
    :param team: team selected (if any)
    :return: query
    """
    # Team Filter
    if team != '':
        return data.filter(team=team)
    else:
        return data


def filter_toi(data, toi):
    """
    Filter by toi minimum 
    :param data: data we have at that point 
    :param toi: toi threshold 
    :return: query
    """
    if toi != 0:
        toi = convert_to_seconds(toi)
        return data.filter(toi__gte=toi)
    else:
        return data


def filter_season_type(data, season_type):
    """
    Filter if Regular Season, Playoffs, or Both
    :param data: data we have at that point 
    :param season_type: Reg, Playoffs, Both
    :return: query
    """
    if season_type == 'Regular Season':
        return data.filter(game_id__lte=21230)

    if season_type == 'Playoffs':
        return data.filter(game_id__gt=21230)

    return data


def filter_venue(data, venue):
    """
    Filter by venue 
    :param data: data we have at that point  
    :param venue: Home, Away, Both
    :return: query
    """
    if venue == "Home":
        return data.filter(team=F('home'))

    if venue == "Away":
        return data.exclude(team=F('home'))

    return data


def filter_by_cumulative(data, toi, adjustment):
    """
    Filter by season
    Also filter by toi here
    :param data: data we have at that point 
    :param toi: toi filter
    :param adjustment: ex: "Score Adjusted"
    :return: list (of dicts) who match criteria
    """
    cols = ['team', 'games', 'goals_a', 'goals_f', 'shots_a', 'shots_f', 'fenwick_a', 'fenwick_f', 'corsi_a', 'corsi_f',
            'pent', 'pend', 'hits_f', 'hits_a', 'gives', 'takes', 'face_l', 'face_w', 'face_off', 'face_def', 'face_neu'
            , 'toi']

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
                      face_off=Sum('face_off'), face_def=Sum('face_def'), face_neu=Sum('face_neu'))
    else:
        data = data.values('team') \
            .annotate(games=Count('game_id', distinct=True), goals_a=Sum('goals_a'), shots_a=Sum('shots_a'),
                      fenwick_a=Sum('fenwick_a'), corsi_a=Sum('corsi_a'), goals_f=Sum('goals_f'), toi=Sum('toi'),
                      shots_f=Sum('shots_f'), fenwick_f=Sum('fenwick_f'), corsi_f=Sum('corsi_f'), pent=Sum('pent'),
                      pend=Sum('pend'), gives=Sum('gives'), takes=Sum('takes'), hits_f=Sum('hits_f'),
                      hits_a=Sum('hits_a'), face_l=Sum('face_l'), face_w=Sum('face_w'), face_off=Sum('face_off'),
                      face_def=Sum('face_def'), face_neu=Sum('face_neu'))

    data = filter_toi(data, toi)

    return list(data.values(*cols))


def filter_by_season(data, toi, adjustment):
    """
    Filter by season
    Also filter by toi here
    :param data: data we have at that point 
    :param toi: toi filter
    :param adjustment: ex: "Score Adjusted"
    :return: list (of dicts) who match criteria
    """
    cols = ['team', 'season', 'games', 'goals_a', 'goals_f', 'shots_a', 'shots_f', 'fenwick_a', 'fenwick_f', 'corsi_a',
            'corsi_f', 'pent', 'pend', 'hits_f', 'hits_a', 'gives', 'takes', 'face_l', 'face_w', 'face_off', 'face_def',
            'face_neu', 'toi']

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
                      face_off=Sum('face_off'), face_def=Sum('face_def'), face_neu=Sum('face_neu'), )
    else:
        data = data.values('team', 'season') \
            .annotate(games=Count('game_id', distinct=True), goals_a=Sum('goals_a'), shots_a=Sum('shots_a'),
                      fenwick_a=Sum('fenwick_a'), corsi_a=Sum('corsi_a'), goals_f=Sum('goals_f'), toi=Sum('toi'),
                      shots_f=Sum('shots_f'), fenwick_f=Sum('fenwick_f'), corsi_f=Sum('corsi_f'), pent=Sum('pent'),
                      pend=Sum('pend'), gives=Sum('gives'), takes=Sum('takes'), hits_f=Sum('hits_f'),
                      hits_a=Sum('hits_a'), face_l=Sum('face_l'), face_w=Sum('face_w'), face_off=Sum('face_off'),
                      face_def=Sum('face_def'), face_neu=Sum('face_neu'))

    data = filter_toi(data, toi)

    return list(data.values(*cols))


def filter_by_game(data, toi, adjustment):
    """
    Filter by game
    Also filter by toi here
    :param data: data we have at that point 
    :param toi: toi filter
    :param adjustment: ex: "Score Adjusted"
    :return: list (of dicts) who match criteria 
    'game_id', 'date', 'opponent'
    """
    cols = ['team', 'season', 'game_id', 'date', 'opponent', 'home', 'goals_a', 'goals_f', 'shots_a', 'shots_f',
            'fenwick_a', 'fenwick_f', 'corsi_a', 'corsi_f', 'pent', 'pend', 'hits_f', 'hits_a', 'gives', 'takes',
            'face_l', 'face_w', 'face_off', 'face_def', 'face_neu', 'toi']

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
                      face_def=Sum('face_def'), face_neu=Sum('face_neu'))
    else:
        data = data.values('team', 'season', 'game_id', 'date', 'opponent', 'home') \
            .annotate(goals_a=Sum('goals_a'), shots_a=Sum('shots_a'), fenwick_a=Sum('fenwick_a'), corsi_a=Sum('corsi_a'),
                      goals_f=Sum('goals_f'), toi=Sum('toi'), shots_f=Sum('shots_f'), fenwick_f=Sum('fenwick_f'),
                      corsi_f=Sum('corsi_f'), pent=Sum('pent'), pend=Sum('pend'), gives=Sum('gives'), takes=Sum('takes'),
                      hits_f=Sum('hits_f'), hits_a=Sum('hits_a'), face_l=Sum('face_l'), face_w=Sum('face_w'),
                      face_off=Sum('face_off'), face_def=Sum('face_def'), face_neu=Sum('face_neu'))

    data = filter_toi(data, toi)

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

    if 'shots_a_raw' in list(team.keys()):
        team['Sv%'] = get_pct(team['shots_a_raw'] - team['goals_a'], team['shots_a_raw'])
        team['Sh%'] = get_pct(team['goals_f'], team['shots_f_raw'])
        team['fSh%'] = get_pct(team['goals_f'], team['fenwick_f_raw'])
        team['FSv%'] = get_pct(team['fenwick_a_raw'] - team['goals_a'], team['fenwick_a_raw'])
        team['Miss%'] = get_pct(team['fenwick_a_raw'] - team['shots_a_raw'], team['fenwick_a_raw'])
    else:
        team['Sv%'] = get_pct(team['shots_a']-team['goals_a'], team['shots_a'])
        team['Sh%'] = get_pct(team['goals_f'], team['shots_f'])
        team['fSh%'] = get_pct(team['goals_f'], team['fenwick_f'])
        team['FSv%'] = get_pct(team['fenwick_a'] - team['goals_a'], team['fenwick_a'])
        team['Miss%'] = get_pct(team['fenwick_a'] - team['shots_a'], team['fenwick_a'])

    team['GF%'] = get_pct(team['goals_f'], team['goals_a'] + team['goals_f'])
    team['FF%'] = get_pct(team['fenwick_f'], team['fenwick_a'] + team['fenwick_f'])
    team['CF%'] = get_pct(team['corsi_f'], team['corsi_a'] + team['corsi_f'])

    team['shots_f_60'] = get_per_60(team['toi'], team['shots_f'])
    team['goals_f_60'] = get_per_60(team['toi'], team['goals_f'])
    team['fenwick_f_60'] = get_per_60(team['toi'], team['fenwick_f'])
    team['corsi_f_60'] = get_per_60(team['toi'], team['corsi_f'])

    team['shots_a_60'] = get_per_60(team['toi'], team['shots_a'])
    team['goals_a_60'] = get_per_60(team['toi'], team['goals_a'])
    team['fenwick_a_60'] = get_per_60(team['toi'], team['fenwick_a'])
    team['corsi_a_60'] = get_per_60(team['toi'], team['corsi_a'])

    if adjustment == 'Score Adjusted':
        team['shots_f'] = format(team['shots_f'], '.2f')
        team['fenwick_f'] = format(team['fenwick_f'], '.2f')
        team['corsi_f'] = format(team['corsi_f'], '.2f')
        team['shots_a'] = format(team['shots_a'], '.2f')
        team['fenwick_a'] = format(team['fenwick_a'], '.2f')
        team['corsi_a'] = format(team['corsi_a'], '.2f')

    return team


def get_pct(numerator, denominator):
    """
    return pct given numerator and denominator
    :param numerator: ...
    :param denominator: ...
    :return: pct 
    """
    try:
        pct = numerator / denominator
    except ZeroDivisionError:
        return ''

    return format(pct*100, '.2f')


def get_per_60(toi, stat):
    """
    Return stat in Per 60
    :param toi: time on ice
    :param stat: given stats (ex: Shots against)
    :return: number/60
    """
    if float(toi) != 0:
        return format(stat*60/(float(toi)), '.2f')
    else:
        return 0


def convert_to_seconds(minutes):
    """
    Convert minutes to seconds
    :param minutes: ex: 500
    :return: seconds
    """
    return int(minutes) * 60



