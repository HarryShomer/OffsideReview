from django.views import generic
from .models import Skaters
from django.http import JsonResponse
from django.db.models import Sum, Count
from helpers.query_helpers import *


class IndexView(generic.ListView):
    """
    Returns just the files for the url
    """
    template_name = 'skaters/index.html'

    def get_queryset(self):
        return []


def get_search_list(request):
    """
    View for getting goalie search list when page loads
    
    :param request: Nothing really 
    
    :return: JsonResponse with goalies
    """
    players = list(Skaters.objects.values_list('player', flat=True))
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
    request_data = parse_query_request(request)

    query = filter_view(request_data['stats_view'])
    query = query.filter(date__range=[request_data['date_filter_from'], request_data['date_filter_to']])
    query = filter_players(query, request_data['search'])
    query = filter_team(query, request_data['team'])
    query = filter_strength(query, request_data['strength'])
    query = filter_season_type(query, request_data['season_type'])
    query = filter_venue(query, request_data['venue'])
    query = filter_position(query, request_data['position'])

    if request_data['stats_view'] == 'Individual':
        skaters = filter_by_individual(query, request_data)
        skaters = [calculate_ind_stats(player, request_data['strength']) for player in skaters]
    elif request_data['stats_view'] == 'On Ice':
        skaters = filter_by_on_ice(query, request_data)
        skaters = [calculate_ice_stats(player, request_data['strength'], request_data['adjustment']) for player in skaters]
    elif request_data['stats_view'] == 'Relative':
        skaters = filter_by_rel(query, request_data)
        skaters = [calculate_rel_stats(player, request_data['strength'], request_data['stats_view']) for player in skaters]
    elif request_data['stats_view'] == 'Zone Starts':
        skaters = filter_by_zone(query, request_data)
        skaters = [calculate_zone_stats(player, request_data['strength']) for player in skaters]
    elif request_data['stats_view'] == 'All':
        skaters = calculate_all_stats(query, request_data)
    else:
        # If you ask for nothing you get nothing
        skaters = dict()

    return JsonResponse({'data': skaters})


def parse_query_request(request):
    """
    Parse the request and store in a dict
    """
    fields = ['strength', 'split_by', 'team', 'search', 'venue', 'season_type', 'date_filter_from', 'date_filter_to',
              'adjustment', 'position', 'toi', 'stats_view']

    return {field: request.GET.get(field) for field in fields}


def filter_view(stats_view):
    """
    Filter by view type 
    
    :param stats_view: -> Individual, On-ice, relative, zone starts
    
    :return: query
    """
    if stats_view == 'Individual':
        return Skaters.objects.values('player', 'player_id', 'position', 'handedness', 'team', 'game_id', 'season', 'date',
                                      'opponent', 'home', 'strength', 'toi_on', 'goals', 'a1', 'a2', 'isf', 'ifen', 'ixg',
                                      'icors', 'iblocks', 'pen_drawn', 'pen_taken', 'gives', 'takes', 'hits_f', 'hits_a',
                                      'ifac_win', 'ifac_loss', 'if_empty', "shooter_ixg")
    elif stats_view == 'On Ice':
        return Skaters.objects.values('player', 'player', 'position', 'handedness', 'team', 'game_id', 'season', 'date',
                                      'opponent', 'home', 'strength', 'toi_on', 'goals_a', 'goals_f', 'shots_f_sa',
                                      'fenwick_f_sa', 'corsi_f_sa', 'shots_a_sa', 'fenwick_a_sa', 'corsi_a_sa',
                                      'shots_f', 'fenwick_f', 'xg_f', 'corsi_f', 'shots_a', 'fenwick_a', 'corsi_a',
                                      'xg_a', 'if_empty', "shooter_xg_f", "shooter_xg_a")
    elif stats_view == 'Relative':
        return Skaters.objects.values('player', 'player', 'position', 'handedness', 'team', 'game_id', 'season', 'date',
                                      'opponent', 'home', 'strength', 'toi_on', 'goals_a', 'goals_f', 'shots_f_sa',
                                      'fenwick_f_sa', 'corsi_f_sa', 'shots_a_sa', 'fenwick_a_sa', 'corsi_a_sa',
                                      'shots_f', 'fenwick_f', 'corsi_f', 'shots_a', 'fenwick_a', 'corsi_a', 'shots_f_off',
                                      'goals_f_off', 'fenwick_f_off', 'corsi_f_off', 'shots_a_off', 'goals_a_off',
                                      'fenwick_a_off', 'corsi_a_off', 'xg_f', 'xg_a', 'xg_f_off', 'xg_a_off',
                                      'shots_f_off_sa', 'fenwick_f_off_sa', 'corsi_f_off_sa', 'shots_a_off_sa',
                                      'fenwick_a_off_sa', 'corsi_a_off_sa', 'toi_off', 'if_empty', "shooter_xg_f",
                                      "shooter_xg_a", "shooter_xg_f_off", "shooter_xg_a_off")
    elif stats_view == 'Zone Starts':
        return Skaters.objects.values('player', 'player', 'position', 'handedness', 'team', 'game_id', 'season', 'date',
                                      'opponent', 'home', 'strength', 'toi_on', 'toi_off', 'face_off', 'face_def',
                                      'face_neu', 'face_off_off', 'face_def_off', 'face_neu_off', 'if_empty')
    elif stats_view == 'All':
        return Skaters.objects.all()


def filter_position(data, position):
    """
    Filter by Position
    
    :param data: data we have at that point  
    :param position: Position...C, RW, LW, D
    
    :return: query
    """
    if position == 'F':
        return data.filter(position__in=['C', 'LW', 'RW'])
    elif position == 'D':
        return data.filter(position='D')
    else:
        return data


def filter_by_individual(data, request_data):
    """
    Filter by season (also filter by toi here)
    
    :param data: data we have at that point 
    :param request_data: data sent from request
    
    :return: list (of dicts) who match criteria
    """
    cols = get_split_type(request_data['split_by'])

    data = data.values(*cols) \
        .annotate(games=Count('game_id', distinct=True), toi_on=Sum('toi_on'), goals=Sum('goals'), a1=Sum('a1'),
                  a2=Sum('a2'), isf=Sum('isf'), ifen=Sum('ifen'), icors=Sum('icors'), ixg=Sum('ixg'), iblocks=Sum('iblocks'),
                  pend=Sum('pen_drawn'), pent=Sum('pen_taken'), gives=Sum('gives'), takes=Sum('takes'), hits_f=Sum('hits_f'),
                  hits_a=Sum('hits_a'), ifac_win=Sum('ifac_win'), ifac_loss=Sum('ifac_loss'), sh_ixg=Sum("shooter_ixg"))

    # Filter TOI
    data = filter_toi(data, request_data['toi'], False)

    # Add in columns for stats
    cols = cols + ['toi_on', 'goals', 'a1', 'a2', 'isf', 'ifen', 'ixg', 'icors', 'iblocks', 'pend', 'pent', 'gives',
                   'takes', 'hits_f', 'hits_a', 'ifac_win', 'ifac_loss', "sh_ixg"]

    # If it isn't by game then we want to know how many games they played during that span
    if request_data['split_by'] != 'Game':
        cols = cols + ['games']

    return list(data.values(*cols))


def filter_by_on_ice(data, request_data):
    """
    Filter by season (also filter by toi here)
    
    :param data: data we have at that point 
    :param request_data: data sent from request
    
    :return: list (of dicts) who match criteria
    """
    cols = get_split_type(request_data['split_by'])

    if request_data['adjustment'] == 'Score Adjusted':
        data = data.values(*cols) \
            .annotate(games=Count('game_id', distinct=True), toi_on=Sum('toi_on'), goals_a=Sum('goals_a'),
                      shots_a_raw=Sum('shots_a'), fenwick_a_raw=Sum('fenwick_a'), shots_f_raw=Sum('shots_f'),
                      fenwick_f_raw=Sum('fenwick_f'), shots_a=Sum('shots_a_sa'), fenwick_a=Sum('fenwick_a_sa'),
                      corsi_a=Sum('corsi_a_sa'), goals_f=Sum('goals_f'), shots_f=Sum('shots_f_sa'), xg_a=Sum('xg_a'),
                      fenwick_f=Sum('fenwick_f_sa'), corsi_f=Sum('corsi_f_sa'), xg_f=Sum('xg_f'),
                      sh_xg_f=Sum('shooter_xg_f'), sh_xg_a=Sum('shooter_xg_a'))

        # These columns are to hold non adjusted numbers for percentages when using score adjusted numbers
        cols = cols + ['shots_f_raw', 'shots_a_raw', 'fenwick_f_raw', 'fenwick_a_raw']
    else:
        data = data.values(*cols) \
            .annotate(games=Count('game_id', distinct=True), toi_on=Sum('toi_on'), goals_a=Sum('goals_a'),
                      shots_a=Sum('shots_a'), fenwick_a=Sum('fenwick_a'), corsi_a=Sum('corsi_a'),  xg_a=Sum('xg_a'),
                      goals_f=Sum('goals_f'), shots_f=Sum('shots_f'), fenwick_f=Sum('fenwick_f'), corsi_f=Sum('corsi_f')
                      , xg_f=Sum('xg_f'), sh_xg_f=Sum('shooter_xg_f'), sh_xg_a=Sum('shooter_xg_a'))

    # Filter TOI
    data = filter_toi(data, request_data['toi'], False)

    # Add in columns for stats
    cols = cols + ['toi_on', 'goals_a', 'goals_f', 'shots_f', 'fenwick_f', 'xg_f', 'corsi_f', 'shots_a', 'fenwick_a',
                   'xg_a', 'corsi_a', "sh_xg_f", "sh_xg_a"]

    # If it isn't by game then we want to know how many games they played during that span
    if request_data['split_by'] != 'Game':
        cols = cols + ['games']

    return list(data.values(*cols))


def filter_by_rel(data, request_data):
    """
    Filter by season (also filter by toi here)
    
    :param data: data we have at that point 
    :param request_data: data sent from request
    
    :return: list (of dicts) who match criteria
    """
    cols = get_split_type(request_data['split_by'])

    if request_data['adjustment'] == 'Score Adjusted':
        data = data.values(*cols) \
            .annotate(games=Count('game_id', distinct=True), toi_on=Sum('toi_on'), goals_a=Sum('goals_a'),
                      shots_a_raw=Sum('shots_a'), fenwick_a_raw=Sum('fenwick_a'), shots_f_raw=Sum('shots_f'),
                      fenwick_f_raw=Sum('fenwick_f'), shots_a_off_raw=Sum('shots_a_off'), shots_f_off_raw=Sum('shots_f_off'),
                      fenwick_a_off_raw=Sum('fenwick_a_off'),  fenwick_f_off_raw=Sum('fenwick_f_off'),
                      shots_a=Sum('shots_a_sa'), fenwick_a=Sum('fenwick_a_sa'), corsi_a=Sum('corsi_a_sa'),
                      goals_f=Sum('goals_f'), shots_f=Sum('shots_f_sa'), fenwick_f=Sum('fenwick_f_sa'),
                      corsi_f=Sum('corsi_f_sa'), goals_a_off=Sum('goals_a_off'), shots_a_off=Sum('shots_a_off_sa'),
                      fenwick_a_off=Sum('fenwick_a_off_sa'), corsi_a_off=Sum('corsi_a_off_sa'),
                      goals_f_off=Sum('goals_f_off'), shots_f_off=Sum('shots_f_off_sa'), toi_off=Sum('toi_off'),
                      fenwick_f_off=Sum('fenwick_f_off_sa'), corsi_f_off=Sum('corsi_f_off_sa'), xg_a=Sum('xg_a'),
                      xg_f=Sum('xg_f'), xg_a_off=Sum('xg_a_off'), xg_f_off=Sum('xg_f_off'), sh_xg_f=Sum('shooter_xg_f'),
                      sh_xg_a=Sum('shooter_xg_a'), sh_xg_f_off=Sum('shooter_xg_f_off'), sh_xg_a_off=Sum('shooter_xg_a_off'))

        # These columns are to hold non adjusted numbers for percentages when using score adjusted numbers
        cols = cols + ['shots_f_raw', 'shots_a_raw', 'fenwick_f_raw', 'fenwick_a_raw', 'shots_f_off_raw',
                       'shots_a_off_raw', 'fenwick_f_off_raw', 'fenwick_a_off_raw']
    else:
        data = data.values(*cols) \
            .annotate(games=Count('game_id', distinct=True), toi_on=Sum('toi_on'), goals_a=Sum('goals_a'),
                      shots_a=Sum('shots_a'), fenwick_a=Sum('fenwick_a'), corsi_a=Sum('corsi_a'),
                      goals_f=Sum('goals_f'), shots_f=Sum('shots_f'), fenwick_f=Sum('fenwick_f'),
                      corsi_f=Sum('corsi_f'), goals_a_off=Sum('goals_a_off'), shots_a_off=Sum('shots_a_off'),
                      fenwick_a_off=Sum('fenwick_a_off'), corsi_a_off=Sum('corsi_a_off'),
                      goals_f_off=Sum('goals_f_off'), shots_f_off=Sum('shots_f_off'), toi_off=Sum('toi_off'),
                      fenwick_f_off=Sum('fenwick_f_off'), corsi_f_off=Sum('corsi_f_off'), xg_a=Sum('xg_a'),
                      xg_f=Sum('xg_f'), xg_a_off=Sum('xg_a_off'), xg_f_off=Sum('xg_f_off'), sh_xg_f=Sum('shooter_xg_f'),
                      sh_xg_a=Sum('shooter_xg_a'), sh_xg_f_off=Sum('shooter_xg_f_off'), sh_xg_a_off=Sum('shooter_xg_a_off'))

    # Filter TOI
    data = filter_toi(data, request_data['toi'], False)

    # Add in columns for stats
    cols = cols + ['toi_on', 'goals_a', 'goals_f', 'shots_f', 'fenwick_f', 'corsi_f', 'shots_a', 'fenwick_a', 'corsi_a',
                   'shots_f_off', 'goals_f_off', 'fenwick_f_off', 'corsi_f_off', 'shots_a_off', 'goals_a_off',
                   'fenwick_a_off', 'corsi_a_off', 'toi_off', 'xg_f', 'xg_a', 'xg_a_off', 'xg_f_off', "sh_xg_f",
                   "sh_xg_a", "sh_xg_f_off", "sh_xg_a_off"]

    # If it isn't by game then we want to know how many games they played during that span
    if request_data['split_by'] != 'Game':
        cols = cols + ['games']

    return list(data.values(*cols))


def filter_by_zone(data, request_data):
    """
    Filter by season (also filter by toi here)
    
    :param data: data we have at that point 
    :param request_data: data sent from request
    
    :return: list (of dicts) who match criteria
    """
    cols = get_split_type(request_data['split_by'])

    data = data.values(*cols) \
        .annotate(games=Count('game_id', distinct=True), toi_on=Sum('toi_on'), face_off=Sum('face_off'),
                  face_def=Sum('face_def'), face_neu=Sum('face_neu'), face_off_off=Sum('face_off_off'),
                  face_def_off=Sum('face_def_off'), face_neu_off=Sum('face_neu_off'), toi_off=Sum('toi_off'))

    # Filter TOI
    data = filter_toi(data, request_data['toi'], False)

    # Add in columns for stats
    cols = cols + ['toi_on', 'toi_off', 'face_off', 'face_def', 'face_neu', 'face_off_off', 'face_def_off', 'face_neu_off']

    # If it isn't by game then we want to know how many games they played during that span
    if request_data['split_by'] != 'Game':
        cols = cols + ['games']

    return list(data.values(*cols))


def calculate_ind_stats(player, strength):
    """
    Calculate statistics for individual view
    
    :param player: given row
    :param strength: on ice strength
    
    :return: json
    """
    player['toi_on'] = format(player['toi_on'] / 60, '.2f')  # Convert to minutes
    player['strength'] = strength

    player['ish%'] = get_pct(player['goals'], player['isf'])
    player['ifsh%'] = get_pct(player['goals'], player['ifen'])
    player['ixfsh%'] = get_pct(player['ixg'], player['ifen'])

    player['assists'] = player['a1'] + player['a2']
    player['p'] = player['assists'] + player['goals']
    player['p1'] = player['a1'] + player['goals']

    player['g60'] = get_per_60(player['toi_on'], player['goals'])
    player['a60'] = get_per_60(player['toi_on'], player['assists'])
    player['a160'] = get_per_60(player['toi_on'], player['a1'])
    player['a260'] = get_per_60(player['toi_on'], player['a2'])
    player['p60'] = get_per_60(player['toi_on'], player['p'])
    player['p160'] = get_per_60(player['toi_on'], player['p1'])
    player['isf60'] = get_per_60(player['toi_on'], player['isf'])
    player['ixg60'] = get_per_60(player['toi_on'], player['ixg'])
    player['ifen60'] = get_per_60(player['toi_on'], player['ifen'])
    player['icors60'] = get_per_60(player['toi_on'], player['icors'])
    player['face%'] = get_pct(player['ifac_win'], player['ifac_win']+player['ifac_loss'])
    player['ixg'] = round(player['ixg'], 2)

    #### Delete Shooter for now #####
    del player['sh_ixg']
    ##################################

    return player


def calculate_ice_stats(player, strength, adjustment):
    """
    Calculate statistics for on ice view
    
    :param player: given row
    :param strength: on ice strength
    :param adjustment: ...
    
    :return json
    """
    player['toi_on'] = format(player['toi_on'] / 60, '.2f')  # Convert to minutes
    player['strength'] = strength

    # If this key is there then numbers are score adjusted so use these fields for percentages
    if 'shots_a_raw' in list(player.keys()):
        player['Sh%'] = get_pct(player['goals_f'], player['shots_f_raw'])
        player['fSh%'] = get_pct(player['goals_f'], player['fenwick_f_raw'])
        player['xFSh%'] = get_pct(player['xg_f'], player['fenwick_f_raw'])

        player['Sv%'] = get_pct(player['shots_a_raw'] - player['goals_a'], player['shots_a_raw'])
        player['FSv%'] = get_pct(player['fenwick_a_raw'] - player['goals_a'], player['fenwick_a_raw'])
        player['xFSv%'] = get_pct(player['fenwick_a_raw'] - player['xg_a'], player['fenwick_a_raw'])
        player['Miss%'] = get_pct(player['fenwick_a_raw'] - player['shots_a_raw'], player['fenwick_a_raw'])
    else:
        player['Sh%'] = get_pct(player['goals_f'], player['shots_f'])
        player['fSh%'] = get_pct(player['goals_f'], player['fenwick_f'])
        player['xFSh%'] = get_pct(player['xg_f'], player['fenwick_f'])

        player['Sv%'] = get_pct(player['shots_a'] - player['goals_a'], player['shots_a'])
        player['FSv%'] = get_pct(player['fenwick_a'] - player['goals_a'], player['fenwick_a'])
        player['xFSv%'] = get_pct(player['fenwick_a'] - player['xg_a'], player['fenwick_a'])
        player['Miss%'] = get_pct(player['fenwick_a'] - player['shots_a'], player['fenwick_a'])

    player['GF%'] = get_pct(player['goals_f'], player['goals_f'] + player['goals_a'])
    player['xGF%'] = get_pct(player['xg_f'], player['xg_f'] + player['xg_a'])
    player['CF%'] = get_pct(player['corsi_f'], player['corsi_f'] + player['corsi_a'])
    player['FF%'] = get_pct(player['fenwick_f'], player['fenwick_f'] + player['fenwick_a'])

    # Weighted Shots
    player['wsh_f'] = player['goals_f'] + .2 * (player['corsi_f'] - player['goals_f'])
    player['wsh_a'] = player['goals_a'] + .2 * (player['corsi_a'] - player['goals_a'])
    player['wshF%'] = get_pct(player['wsh_f'], player['wsh_f'] + player['wsh_a'])

    player['shots_f_60'] = get_per_60(player['toi_on'], player['shots_f'])
    player['goals_f_60'] = get_per_60(player['toi_on'], player['goals_f'])
    player['fenwick_f_60'] = get_per_60(player['toi_on'], player['fenwick_f'])
    player['wsh_f_60'] = get_per_60(player['toi_on'], player['wsh_f'])
    player['xg_f_60'] = get_per_60(player['toi_on'], player['xg_f'])
    player['corsi_f_60'] = get_per_60(player['toi_on'], player['corsi_f'])
    player['shots_a_60'] = get_per_60(player['toi_on'], player['shots_a'])
    player['goals_a_60'] = get_per_60(player['toi_on'], player['goals_a'])
    player['fenwick_a_60'] = get_per_60(player['toi_on'], player['fenwick_a'])
    player['wsh_a_60'] = get_per_60(player['toi_on'], player['wsh_a'])
    player['xg_a_60'] = get_per_60(player['toi_on'], player['xg_a'])
    player['corsi_a_60'] = get_per_60(player['toi_on'], player['corsi_a'])

    # Because score adjusted numbers aren't integers
    if adjustment == 'Score Adjusted':
        player['shots_f'] = format(player['shots_f'], '.2f')
        player['fenwick_f'] = format(player['fenwick_f'], '.2f')
        player['corsi_f'] = format(player['corsi_f'], '.2f')
        player['shots_a'] = format(player['shots_a'], '.2f')
        player['fenwick_a'] = format(player['fenwick_a'], '.2f')
        player['corsi_a'] = format(player['corsi_a'], '.2f')

    player['xg_f'] = round(player['xg_f'], 2)
    player['xg_a'] = round(player['xg_a'], 2)
    player['wsh_f'] = round(player['wsh_f'], 2)
    player['wsh_a'] = round(player['wsh_a'], 2)

    #### Delete Shooter for now #####
    del player['sh_xg_f'], player['sh_xg_a']
    ##################################

    return player


def calculate_rel_stats(player, strength, query_type):
    """
    Calculate statistics for rel view
    
    :param player: given row
    :param strength: on ice strength
    :param query_type: If this is just a "Relative" or stemming from "All"
    
    :return json
    """
    player['toi_on'] = format(player['toi_on'] / 60, '.2f')  # Convert to minutes
    player['toi_off'] = format(player['toi_off'] / 60, '.2f')  # Convert to minutes
    player['strength'] = strength

    # Get wsh stuff
    player['wsh_f'] = player['goals_f'] + .2 * (player['corsi_f'] - player['goals_f'])
    player['wsh_a'] = player['goals_a'] + .2 * (player['corsi_a'] - player['goals_a'])
    player['wsh_f_off'] = player['goals_f_off'] + .2 * (player['corsi_f_off'] - player['goals_f_off'])
    player['wsh_a_off'] = player['goals_a_off'] + .2 * (player['corsi_a_off'] - player['goals_a_off'])

    """
    Get off-ice stats for each category
    """
    gf_pct_off = get_pct(player['goals_f_off'], player['goals_f_off'] + player['goals_a_off'])
    cf_pct_off = get_pct(player['corsi_f_off'], player['corsi_f_off'] + player['corsi_a_off'])
    ff_pct_off = get_pct(player['fenwick_f_off'], player['fenwick_f_off'] + player['fenwick_a_off'])
    wsh_pct_off = get_pct(player['wsh_f_off'], player['wsh_f_off'] + player['wsh_a_off'])
    xg_pct_off = get_pct(player['xg_f_off'], player['xg_f_off'] + player['xg_a_off'])

    shots_f_60_off = get_per_60(player['toi_off'], player['shots_f_off'])
    goals_f_60_off = get_per_60(player['toi_off'], player['goals_f_off'])
    fenwick_f_60_off = get_per_60(player['toi_off'], player['fenwick_f_off'])
    wsh_f_60_off = get_per_60(player['toi_off'], player['wsh_f_off'])
    xg_f_60_off = get_per_60(player['toi_off'], player['xg_f_off'])
    corsi_f_60_off = get_per_60(player['toi_off'], player['corsi_f_off'])

    shots_a_60_off = get_per_60(player['toi_off'], player['shots_a_off'])
    goals_a_60_off = get_per_60(player['toi_off'], player['goals_a_off'])
    fenwick_a_60_off = get_per_60(player['toi_off'], player['fenwick_a_off'])
    wsh_a_60_off = get_per_60(player['toi_off'], player['wsh_a_off'])
    xg_a_60_off = get_per_60(player['toi_off'], player['xg_a_off'])
    corsi_a_60_off = get_per_60(player['toi_off'], player['corsi_a_off'])

    # If this key then numbers are score adjusted so use these fields for percentages
    if 'shots_a_off_raw' in list(player.keys()):
        sh_pct_off = get_pct(player['goals_a_off'], player['shots_f_off_raw'])
        fsh_pct_off = get_pct(player['goals_f_off'], player['fenwick_f_off_raw'])
        xfsh_pct_off = get_pct(player['xg_f_off'], player['fenwick_f_off_raw'])
        sv_pct_off = get_pct(player['shots_a_off_raw'] - player['goals_a_off'], player['shots_a_off_raw'])
        fsv_pct_off = get_pct(player['fenwick_a_off_raw'] - player['goals_a_off'], player['fenwick_a_off_raw'])
        xfsv_pct_off = get_pct(player['fenwick_a_off_raw'] - player['xg_a_off'], player['fenwick_a_off_raw'])
        miss_pct_off = get_pct(player['fenwick_a_off_raw'] - player['shots_a_off_raw'], player['fenwick_a_off_raw'])
    else:
        sh_pct_off = get_pct(player['goals_a_off'], player['shots_f_off'])
        fsh_pct_off = get_pct(player['goals_f_off'], player['fenwick_f_off'])
        xfsh_pct_off = get_pct(player['xg_f_off'], player['fenwick_f_off'])
        sv_pct_off = get_pct(player['shots_a_off'] - player['goals_a_off'], player['shots_a_off'])
        fsv_pct_off = get_pct(player['fenwick_a_off'] - player['goals_a_off'], player['fenwick_a_off'])
        xfsv_pct_off = get_pct(player['fenwick_a_off'] - player['xg_a_off'], player['fenwick_a_off'])
        miss_pct_off = get_pct(player['fenwick_a_off'] - player['shots_a_off'], player['fenwick_a_off'])

    """
    Calculate Statistics
    """
    player['GF%_rel'] = get_rel(get_pct(player['goals_f'], player['goals_f'] + player['goals_a']), gf_pct_off)
    player['CF%_rel'] = get_rel(get_pct(player['corsi_f'], player['corsi_f'] + player['corsi_a']), cf_pct_off)
    player['FF%_rel'] = get_rel(get_pct(player['fenwick_f'], player['fenwick_f'] + player['fenwick_a']), ff_pct_off)
    player['wshF%_rel'] = get_rel(get_pct(player['wsh_f'], player['wsh_f'] + player['wsh_a']), wsh_pct_off)
    player['xGF%_rel'] = get_rel(get_pct(player['xg_f'], player['xg_f'] + player['xg_a']), xg_pct_off)

    player['shots_f_60_rel'] = get_rel(get_per_60(player['toi_on'], player['shots_f']), shots_f_60_off)
    player['goals_f_60_rel'] = get_rel(get_per_60(player['toi_on'], player['goals_f']), goals_f_60_off)
    player['fenwick_f_60_rel'] = get_rel(get_per_60(player['toi_on'], player['fenwick_f']), fenwick_f_60_off)
    player['wsh_f_60_rel'] = get_rel(get_per_60(player['toi_on'], player['wsh_f']), wsh_f_60_off)
    player['xg_f_60_rel'] = get_rel(get_per_60(player['toi_on'], player['xg_f']), xg_f_60_off)
    player['corsi_f_60_rel'] = get_rel(get_per_60(player['toi_on'], player['corsi_f']), corsi_f_60_off)

    player['shots_a_60_rel'] = get_rel(get_per_60(player['toi_on'], player['shots_a']), shots_a_60_off)
    player['goals_a_60_rel'] = get_rel(get_per_60(player['toi_on'], player['goals_a']), goals_a_60_off)
    player['fenwick_a_60_rel'] = get_rel(get_per_60(player['toi_on'], player['fenwick_a']), fenwick_a_60_off)
    player['wsh_a_60_rel'] = get_rel(get_per_60(player['toi_on'], player['wsh_a']), wsh_a_60_off)
    player['xg_a_60_rel'] = get_rel(get_per_60(player['toi_on'], player['xg_a']), xg_a_60_off)
    player['corsi_a_60_rel'] = get_rel(get_per_60(player['toi_on'], player['corsi_a']), corsi_a_60_off)

    # If this key then numbers are score adjusted so use these fields for percentages
    if 'shots_a_off_raw' in list(player.keys()):
        player['Sh%_rel'] = get_rel(get_pct(player['goals_f'], player['shots_f_raw']), sh_pct_off)
        player['fSh%_rel'] = get_rel(get_pct(player['goals_f'], player['fenwick_f_raw']), fsh_pct_off)
        player['xfSh%_rel'] = get_rel(get_pct(player['xg_f'], player['fenwick_f_raw']), xfsh_pct_off)
        player['Sv%_rel'] = get_rel(get_pct(player['shots_a_raw'] - player['goals_a'], player['shots_a_raw']),sv_pct_off)
        player['FSv%_rel'] = get_rel(get_pct(player['fenwick_a_raw'] - player['goals_a'], player['fenwick_a_raw']),fsv_pct_off)
        player['xFSv%_rel'] = get_rel(get_pct(player['fenwick_a_raw'] - player['xg_a'], player['fenwick_a_raw']),xfsv_pct_off)
        player['Miss%_rel'] = get_rel(get_pct(player['fenwick_a_raw'] - player['shots_a_raw'], player['fenwick_a_raw']),miss_pct_off)
    else:
        player['Sh%_rel'] = get_rel(get_pct(player['goals_f'], player['shots_f']), sh_pct_off)
        player['fSh%_rel'] = get_rel(get_pct(player['goals_f'], player['fenwick_f']), fsh_pct_off)
        player['xfSh%_rel'] = get_rel(get_pct(player['xg_f'], player['fenwick_f']), xfsh_pct_off)
        player['Sv%_rel'] = get_rel(get_pct(player['shots_a'] - player['goals_a'], player['shots_a']), sv_pct_off)
        player['FSv%_rel'] = get_rel(get_pct(player['fenwick_a'] - player['goals_a'], player['fenwick_a']), fsv_pct_off)
        player['xFSv%_rel'] = get_rel(get_pct(player['fenwick_a'] - player['xg_a'], player['fenwick_a']), xfsv_pct_off)
        player['Miss%_rel'] = get_rel(get_pct(player['fenwick_a'] - player['shots_a'], player['fenwick_a']),
                                      miss_pct_off)

    # Holds columns for "off" stats
    off_cols = ['xg_f_off', 'corsi_f_off', 'xg_a_off', 'corsi_a_off', 'wsh_f_off', 'wsh_a_off', 'shots_f_off',
                'shots_a_off', 'fenwick_f_off', 'fenwick_a_off']

    # Columns I want to delete...they don't need to be sent to anyone here
    del_cols = ['goals_f', 'shots_f', 'fenwick_f', 'wsh_f', 'xg_f', 'corsi_f', 'goals_a', 'shots_a', 'fenwick_a', 'wsh_a',
                'xg_a', 'corsi_a']

    # If this originates from "All" we want to keep the off columns and round them
    # If this originates from "Relative" we want to also get rid of the off columns
    if query_type == "All":
        for col in off_cols:
            player[col] = round(player[col], 2)
    else:
        del_cols += off_cols

    for col in del_cols:
        del player[col]

    if 'shots_a_off_raw' in list(player.keys()):
        del player['shots_a_off_raw'], player['fenwick_a_off_raw'], player['shots_f_off_raw'], player['fenwick_f_off_raw']

    #### Delete Shooter for now #####
    del player['sh_xg_f'], player['sh_xg_a'], player['sh_xg_f_off'], player['sh_xg_a_off']
    ##################################

    return player


def calculate_zone_stats(player, strength):
    """
    Calculate statistics for zone view
    :param player: given row
    :param strength: on ice strength
    :return json
    """
    player['toi_on'] = format(player['toi_on'] / 60, '.2f')  # Convert to minutes
    player['strength'] = strength

    player['off_zone%'] = get_pct(player['face_off'], player['face_off'] + player['face_def'] + player['face_neu'])
    player['def_zone%'] = get_pct(player['face_def'], player['face_off'] + player['face_def'] + player['face_neu'])
    player['neu_zone%'] = get_pct(player['face_neu'], player['face_off'] + player['face_def'] + player['face_neu'])

    off_zone_pct_off = get_pct(player['face_off_off'], player['face_off_off'] + player['face_def_off']+player['face_neu_off'])
    neu_zone_pct_off = get_pct(player['face_neu_off'], player['face_off_off'] + player['face_def_off'] + player['face_neu_off'])
    def_zone_pct_off = get_pct(player['face_def_off'], player['face_off_off'] + player['face_def_off'] + player['face_neu_off'])

    player['off_zone%_rel'] = get_rel(player['off_zone%'], off_zone_pct_off)
    player['def_zone%_rel'] = get_rel(player['def_zone%'], def_zone_pct_off)
    player['neu_zone%_rel'] = get_rel(player['neu_zone%'], neu_zone_pct_off)

    return player


def calculate_all_stats(query, request_data):
    """
    Calculate ALL Stats for the players
    """
    import operator

    # How to sort depends on how we want to split it
    if request_data['split_by'] == 'Game':
        sorting_keys = operator.itemgetter("player", "player_id", "season", "game_id")
    elif request_data['split_by'] == 'Season':
        sorting_keys = operator.itemgetter("player", "player_id", "season", "team")
    else:
        # Cumulative
        sorting_keys = operator.itemgetter("player", "player_id", "team")

    # Get Stats for each type
    ind = [calculate_ind_stats(player, request_data['strength']) for player in filter_by_individual(query, request_data)]
    ice = [calculate_ice_stats(player, request_data['strength'], request_data['adjustment']) for player in filter_by_on_ice(query, request_data)]
    rel = [calculate_rel_stats(player, request_data['strength'], "All") for player in filter_by_rel(query, request_data)]
    zone = [calculate_zone_stats(player, request_data['strength']) for player in filter_by_zone(query, request_data)]

    # Merge dictionaries
    for i, o, r, z in zip(sorted(ind, key=sorting_keys), sorted(ice, key=sorting_keys), sorted(rel, key=sorting_keys), sorted(zone, key=sorting_keys)):
        i.update(o), i.update(r), i.update(z)

        # TODO: Figure out why 'toi_off' is 60x higher than it should be
        i['toi_off'] = round(i['toi_off']/60, 2)

    return ind


def get_split_type(split_by):
    """
    Return base columns for split type
    
    :param split_by: Season, Cumulative, Game
    
    :return: base cols
    """
    if split_by == 'Season':
        return ['player', 'player_id', 'season', 'team', 'position', 'handedness']
    elif split_by == 'Cumulative':
        return ['player', 'player_id', 'team', 'position', 'handedness']
    else:
        return ['player', 'player_id', 'season', 'game_id', 'team', 'date', 'opponent', 'home', 'position', 'handedness']


def get_rel(on, off):
    """
    Get rel of player's numbers
    
    :param on: stats on ice
    :param off: stats off ice
    
    :return: rel
    """
    try:
        return format(float(on) - float(off), '.2f')
    except (TypeError, ValueError):
        return ''




