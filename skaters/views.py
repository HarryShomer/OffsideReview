from django.views import generic
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.db.models import F
from .models import Skaters
from django.core import serializers


class IndexView(generic.ListView):
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
    response = {'search_list': players}

    return JsonResponse(response)


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
    position = request.GET.get('position')
    stats_view = request.GET.get('stats_view')

    query = filter_view(stats_view)
    query = query.filter(date__range=[date_filter_from, date_filter_to])
    query = filter_player(query, player_search)
    query = filter_team(query, team)
    query = filter_strength(query, strength)
    query = filter_season_type(query, season_type)
    query = filter_venue(query, venue)
    query = filter_position(query, position)

    if stats_view == 'Individual':
        players = filter_by_individual(query, toi, split_by)
        players = [calculate_ind_stats(player, strength) for player in players]
    elif stats_view == 'On Ice':
        players = filter_by_on_ice(query, toi, adjustment, split_by)
        players = [calculate_ice_stats(player, strength, adjustment) for player in players]
    elif stats_view == 'Relative':
        players = filter_by_rel(query, toi, adjustment, split_by)
        players = [calculate_rel_stats(player, strength) for player in players]
    else:
        players = filter_by_zone(query, toi, split_by)
        players = [calculate_zone_stats(player, strength) for player in players]

    response = {'data': players}
    return JsonResponse(response)


def filter_view(stats_view):
    """
    Filter by view type 
    :param stats_view: -> Individual, On-ice, relative, zone starts
    :return: query
    """
    if stats_view == 'Individual':
        return Skaters.objects.values('player', 'player_id', 'position', 'handedness', 'team', 'game_id', 'season', 'date',
                                      'opponent', 'home', 'strength', 'toi_on', 'goals', 'a1', 'a2', 'isf', 'ifen',
                                      'icors', 'iblocks', 'pen_drawn', 'pen_taken', 'gives', 'takes', 'hits_f', 'hits_a',
                                      'ifac_win', 'ifac_loss', 'if_empty')
    elif stats_view == 'On Ice':
        return Skaters.objects.values('player', 'player', 'position', 'handedness', 'team', 'game_id', 'season', 'date',
                                      'opponent', 'home', 'strength', 'toi_on', 'goals_a', 'goals_f', 'shots_f_sa',
                                      'fenwick_f_sa', 'corsi_f_sa', 'shots_a_sa', 'fenwick_a_sa', 'corsi_a_sa',
                                      'shots_f', 'fenwick_f', 'corsi_f', 'shots_a', 'fenwick_a', 'corsi_a', 'if_empty')
    elif stats_view == 'Relative':
        return Skaters.objects.values('player', 'player', 'position', 'handedness', 'team', 'game_id', 'season', 'date',
                                      'opponent', 'home', 'strength', 'toi_on', 'goals_a', 'goals_f', 'shots_f_sa',
                                      'fenwick_f_sa', 'corsi_f_sa', 'shots_a_sa', 'fenwick_a_sa', 'corsi_a_sa',
                                      'shots_f', 'fenwick_f', 'corsi_f', 'shots_a', 'fenwick_a', 'corsi_a', 'shots_f_off',
                                      'goals_f_off', 'fenwick_f_off', 'corsi_f_off', 'shots_a_off', 'goals_a_off',
                                      'fenwick_a_off', 'corsi_a_off', 'shots_f_off_sa', 'fenwick_f_off_sa', 'corsi_f_off_sa',
                                      'shots_a_off_sa', 'fenwick_a_off_sa', 'corsi_a_off_sa', 'toi_off', 'if_empty')
    else:
        return Skaters.objects.values('player', 'player', 'position', 'handedness', 'team', 'game_id', 'season', 'date',
                                      'opponent', 'home', 'strength', 'toi_on', 'toi_off', 'face_off', 'face_def',
                                      'face_neu', 'face_off_off', 'face_def_off', 'face_neu_off', 'if_empty')


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
        return data


def filter_player(data, player):
    """
    Filter by player searched
    :param data: data we have at that point
    :param player: player...
    :return: query
    """
    if player != '':
        return data.filter(player=player)
    else:
        return data


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
        return data.filter(toi_on__gte=toi)
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


def filter_by_individual(data, toi, split_by):
    """
    Filter by season
    Also filter by toi here
    :param data: data we have at that point 
    :param toi: toi filter
    :param split_by: game, season, or cumulative
    :return: list (of dicts) who match criteria
    """
    if split_by == 'Season':
        cols = ['player', 'player_id', 'season', 'team', 'position', 'handedness']
    elif split_by == 'Cumulative':
        cols = ['player', 'player_id', 'team', 'position', 'handedness']
    else:
        cols = ['player', 'player_id', 'season', 'game_id', 'team', 'date', 'opponent', 'home', 'position', 'handedness']

    data = data.values(*cols) \
        .annotate(games=Count('game_id', distinct=True), toi_on=Sum('toi_on'), goals=Sum('goals'), a1=Sum('a1'),
                  a2=Sum('a2'), isf=Sum('isf'), ifen=Sum('ifen'), icors=Sum('icors'), iblocks=Sum('iblocks'),
                  pend=Sum('pen_drawn'), pent=Sum('pen_taken'), gives=Sum('gives'), takes=Sum('takes'),
                  hits_f=Sum('hits_f'), hits_a=Sum('hits_a'), ifac_win=Sum('ifac_win'), ifac_loss=Sum('ifac_loss'))

    # Filter TOI
    data = filter_toi(data, toi)

    cols = cols + ['toi_on', 'goals', 'a1', 'a2', 'isf', 'ifen', 'icors', 'iblocks', 'pend', 'pent', 'gives',
                   'takes', 'hits_f', 'hits_a', 'ifac_win', 'ifac_loss']

    if split_by != 'Game':
        cols = cols + ['games']

    return list(data.values(*cols))


def filter_by_on_ice(data, toi, adjustment, split_by):
    """
    Filter by season
    Also filter by toi here
    :param data: data we have at that point 
    :param toi: toi filter
    :param adjustment: ex: "Score Adjusted"
    :param split_by: game, season, or cumulative
    :return: list (of dicts) who match criteria
    """
    if split_by == 'Season':
        cols = ['player', 'player_id', 'season', 'team', 'position', 'handedness']
    elif split_by == 'Cumulative':
        cols = ['player', 'player_id', 'team', 'position', 'handedness']
    else:
        cols = ['player', 'player_id', 'season', 'game_id', 'team', 'date', 'opponent', 'home', 'position', 'handedness']

    if adjustment == 'Score Adjusted':
        data = data.values(*cols) \
            .annotate(games=Count('game_id', distinct=True), toi_on=Sum('toi_on'), goals_a=Sum('goals_a'),
                      shots_a_raw=Sum('shots_a'), fenwick_a_raw=Sum('fenwick_a'), shots_f_raw=Sum('shots_f'),
                      fenwick_f_raw=Sum('fenwick_f'), shots_a=Sum('shots_a_sa'), fenwick_a=Sum('fenwick_a_sa'),
                      corsi_a=Sum('corsi_a_sa'), goals_f=Sum('goals_f'), shots_f=Sum('shots_f_sa'),
                      fenwick_f=Sum('fenwick_f_sa'), corsi_f=Sum('corsi_f_sa'))

        # These columns are to hold non adjusted numbers for percentages when using score adjusted numbers
        cols = cols + ['shots_f_raw', 'shots_a_raw', 'fenwick_f_raw', 'fenwick_a_raw']
    else:
        data = data.values(*cols) \
            .annotate(games=Count('game_id', distinct=True), toi_on=Sum('toi_on'), goals_a=Sum('goals_a'),
                      shots_a=Sum('shots_a'), fenwick_a=Sum('fenwick_a'), corsi_a=Sum('corsi_a'), goals_f=Sum('goals_f')
                      , shots_f=Sum('shots_f'), fenwick_f=Sum('fenwick_f'), corsi_f=Sum('corsi_f'))

    # Filter TOI
    data = filter_toi(data, toi)

    cols = cols + ['toi_on', 'goals_a', 'goals_f', 'shots_f', 'fenwick_f', 'corsi_f', 'shots_a', 'fenwick_a', 'corsi_a']
    if split_by != 'Game':
        cols = cols + ['games']

    return list(data.values(*cols))


def filter_by_rel(data, toi, adjustment, split_by):
    """
    Filter by season
    Also filter by toi here
    :param data: data we have at that point 
    :param toi: toi filter
    :param adjustment: ex: "Score Adjusted"
    :param split_by: game, season, or cumulative
    :return: list (of dicts) who match criteria
    """

    if split_by == 'Season':
        cols = ['player', 'player_id', 'season', 'team', 'position', 'handedness']
    elif split_by == 'Cumulative':
        cols = ['player', 'player_id', 'team', 'position', 'handedness']
    else:
        cols = ['player', 'player_id', 'season', 'game_id', 'team', 'date', 'opponent', 'home', 'position', 'handedness']

    if adjustment == 'Score Adjusted':
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
                      fenwick_f_off=Sum('fenwick_f_off_sa'), corsi_f_off=Sum('corsi_f_off_sa'))

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
                      fenwick_f_off=Sum('fenwick_f_off'), corsi_f_off=Sum('corsi_f_off'))

    # Filter TOI
    data = filter_toi(data, toi)

    cols = cols + ['toi_on', 'goals_a', 'goals_f', 'shots_f', 'fenwick_f', 'corsi_f', 'shots_a', 'fenwick_a', 'corsi_a',
                   'shots_f_off', 'goals_f_off', 'fenwick_f_off', 'corsi_f_off', 'shots_a_off', 'goals_a_off',
                   'fenwick_a_off', 'corsi_a_off', 'toi_off']

    if split_by != 'Game':
        cols = cols + ['games']

    return list(data.values(*cols))


def filter_by_zone(data, toi, split_by):
    """
    Filter by season
    Also filter by toi here
    :param data: data we have at that point 
    :param toi: toi filter
    :param split_by: game, season, or cumulative
    :return: list (of dicts) who match criteria
    """
    if split_by == 'Season':
        cols = ['player', 'player_id', 'season', 'team', 'position', 'handedness']
    elif split_by == 'Cumulative':
        cols = ['player', 'player_id', 'team', 'position', 'handedness']
    else:
        cols = ['player', 'player_id', 'season', 'game_id', 'team', 'date', 'opponent', 'home', 'position', 'handedness']

    data = data.values(*cols) \
        .annotate(games=Count('game_id', distinct=True), toi_on=Sum('toi_on'), face_off=Sum('face_off'),
                  face_def=Sum('face_def'), face_neu=Sum('face_neu'), face_off_off=Sum('face_off_off'),
                  face_def_off=Sum('face_def_off'), face_neu_off=Sum('face_neu_off'), toi_off=Sum('toi_off'))

    # Filter TOI
    data = filter_toi(data, toi)

    cols = cols + ['toi_on', 'toi_off', 'face_off', 'face_def', 'face_neu', 'face_off_off', 'face_def_off', 'face_neu_off']
    if split_by != 'Game':
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
    player['ifen60'] = get_per_60(player['toi_on'], player['ifen'])
    player['icors60'] = get_per_60(player['toi_on'], player['icors'])
    player['face%'] = get_pct(player['ifac_win'], player['ifac_win']+player['ifac_loss'])

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

    # If this key then numbers are score adjusted so use these fields for percentages
    if 'shots_a_raw' in list(player.keys()):
        player['Sh%'] = get_pct(player['goals_f'], player['shots_f_raw'])
        player['fSh%'] = get_pct(player['goals_f'], player['fenwick_f_raw'])
        player['Sv%'] = get_pct(player['shots_a_raw'] - player['goals_a'], player['shots_a_raw'])
        player['FSv%'] = get_pct(player['fenwick_a_raw'] - player['goals_a'], player['fenwick_a_raw'])
        player['Miss%'] = get_pct(player['fenwick_a_raw'] - player['shots_a_raw'], player['fenwick_a_raw'])
    else:
        player['Sh%'] = get_pct(player['goals_f'], player['shots_f'])
        player['fSh%'] = get_pct(player['goals_f'], player['fenwick_f'])
        player['Sv%'] = get_pct(player['shots_a'] - player['goals_a'], player['shots_a'])
        player['FSv%'] = get_pct(player['fenwick_a'] - player['goals_a'], player['fenwick_a'])
        player['Miss%'] = get_pct(player['fenwick_a'] - player['shots_a'], player['fenwick_a'])

    player['GF%'] = get_pct(player['goals_f'], player['goals_f']+player['goals_a'])
    player['CF%'] = get_pct(player['corsi_f'], player['corsi_f']+player['corsi_a'])
    player['FF%'] = get_pct(player['fenwick_f'], player['fenwick_f']+player['fenwick_a'])

    player['shots_f_60'] = get_per_60(player['toi_on'], player['shots_f'])
    player['goals_f_60'] = get_per_60(player['toi_on'], player['goals_f'])
    player['fenwick_f_60'] = get_per_60(player['toi_on'], player['fenwick_f'])
    player['corsi_f_60'] = get_per_60(player['toi_on'], player['corsi_f'])
    player['shots_a_60'] = get_per_60(player['toi_on'], player['shots_a'])
    player['goals_a_60'] = get_per_60(player['toi_on'], player['goals_a'])
    player['fenwick_a_60'] = get_per_60(player['toi_on'], player['fenwick_a'])
    player['corsi_a_60'] = get_per_60(player['toi_on'], player['corsi_a'])

    if adjustment == 'Score Adjusted':
        player['shots_f'] = format(player['shots_f'], '.2f')
        player['fenwick_f'] = format(player['fenwick_f'], '.2f')
        player['corsi_f'] = format(player['corsi_f'], '.2f')
        player['shots_a'] = format(player['shots_a'], '.2f')
        player['fenwick_a'] = format(player['fenwick_a'], '.2f')
        player['corsi_a'] = format(player['corsi_a'], '.2f')

    return player


def calculate_rel_stats(player, strength):
    """
    Calculate statistics for rel view
    :param player: given row
    :param strength: on ice strength
    :return json
    """
    player['toi_on'] = format(player['toi_on'] / 60, '.2f')    # Convert to minutes
    player['toi_off'] = format(player['toi_off'] / 60, '.2f')  # Convert to minutes
    player['strength'] = strength

    """
    Get off-ice stats for each category
    """
    gf_pct_off = get_pct(player['goals_f_off'], player['goals_f_off'] + player['goals_a_off'])
    cf_pct_off = get_pct(player['corsi_f_off'], player['corsi_f_off'] + player['corsi_a_off'])
    ff_pct_off = get_pct(player['fenwick_f_off'], player['fenwick_f_off'] + player['fenwick_a_off'])
    shots_f_60_off = get_per_60(player['toi_off'], player['shots_f_off'])
    goals_f_60_off = get_per_60(player['toi_off'], player['goals_f_off'])
    fenwick_f_60_off = get_per_60(player['toi_off'], player['fenwick_f_off'])
    corsi_f_60_off = get_per_60(player['toi_off'], player['corsi_f_off'])
    shots_a_60_off = get_per_60(player['toi_off'], player['shots_a_off'])
    goals_a_60_off = get_per_60(player['toi_off'], player['goals_a_off'])
    fenwick_a_60_off = get_per_60(player['toi_off'], player['fenwick_a_off'])
    corsi_a_60_off = get_per_60(player['toi_off'], player['corsi_a_off'])

    # If this key then numbers are score adjusted so use these fields for percentages
    if 'shots_a_off_raw' in list(player.keys()):
        sh_pct_off = get_pct(player['goals_a_off'], player['shots_f_off_raw'])
        fsh_pct_off = get_pct(player['goals_f_off'], player['fenwick_f_off_raw'])
        sv_pct_off = get_pct(player['shots_a_off_raw'] - player['goals_a_off'], player['shots_a_off_raw'])
        fsv_pct_off = get_pct(player['fenwick_a_off_raw'] - player['goals_a_off'], player['fenwick_a_off_raw'])
        miss_pct_off = get_pct(player['fenwick_a_off_raw'] - player['shots_a_off_raw'], player['fenwick_a_off_raw'])
    else:
        sh_pct_off = get_pct(player['goals_a_off'], player['shots_f_off'])
        fsh_pct_off = get_pct(player['goals_f_off'], player['fenwick_f_off'])
        sv_pct_off = get_pct(player['shots_a_off'] - player['goals_a_off'], player['shots_a_off'])
        fsv_pct_off = get_pct(player['fenwick_a_off'] - player['goals_a_off'], player['fenwick_a_off'])
        miss_pct_off = get_pct(player['fenwick_a_off'] - player['shots_a_off'], player['fenwick_a_off'])

    """
    Calculate Statistics
    """
    player['GF%_rel'] = get_rel(get_pct(player['goals_f'], player['goals_f'] + player['goals_a']), gf_pct_off)
    player['CF%_rel'] = get_rel(get_pct(player['corsi_f'], player['corsi_f'] + player['corsi_a']), cf_pct_off)
    player['FF%_rel'] = get_rel(get_pct(player['fenwick_f'], player['fenwick_f'] + player['fenwick_a']), ff_pct_off)

    player['shots_f_60_rel'] = get_rel(get_per_60(player['toi_on'], player['shots_f']), shots_f_60_off)
    player['goals_f_60_rel'] = get_rel(get_per_60(player['toi_on'], player['goals_f']), goals_f_60_off)
    player['fenwick_f_60_rel'] = get_rel(get_per_60(player['toi_on'], player['fenwick_f']), fenwick_f_60_off)
    player['corsi_f_60_rel'] = get_rel(get_per_60(player['toi_on'], player['corsi_f']), corsi_f_60_off)
    player['shots_a_60_rel'] = get_rel(get_per_60(player['toi_on'], player['shots_a']), shots_a_60_off)
    player['goals_a_60_rel'] = get_rel(get_per_60(player['toi_on'], player['goals_a']), goals_a_60_off)
    player['fenwick_a_60_rel'] = get_rel(get_per_60(player['toi_on'], player['fenwick_a']), fenwick_a_60_off)
    player['corsi_a_60_rel'] = get_rel(get_per_60(player['toi_on'], player['corsi_a']), corsi_a_60_off)

    # If this key then numbers are score adjusted so use these fields for percentages
    if 'shots_a_off_raw' in list(player.keys()):
        player['Sh%_rel'] = get_rel(get_pct(player['goals_f'], player['shots_f_raw']), sh_pct_off)
        player['fSh%_rel'] = get_rel(get_pct(player['goals_f'], player['fenwick_f_raw']), fsh_pct_off)
        player['Sv%_rel'] = get_rel(get_pct(player['shots_a_raw'] - player['goals_a'], player['shots_a_raw']), sv_pct_off)
        player['FSv%_rel'] = get_rel(get_pct(player['fenwick_a_raw'] - player['goals_a'], player['fenwick_a_raw']), fsv_pct_off)
        player['Miss%_rel'] = get_rel(get_pct(player['fenwick_a_raw'] - player['shots_a_raw'], player['fenwick_a_raw']), miss_pct_off)
    else:
        player['Sh%_rel'] = get_rel(get_pct(player['goals_f'], player['shots_f']), sh_pct_off)
        player['fSh%_rel'] = get_rel(get_pct(player['goals_f'], player['fenwick_f']), fsh_pct_off)
        player['Sv%_rel'] = get_rel(get_pct(player['shots_a'] - player['goals_a'], player['shots_a']), sv_pct_off)
        player['FSv%_rel'] = get_rel(get_pct(player['fenwick_a'] - player['goals_a'], player['fenwick_a']), fsv_pct_off)
        player['Miss%_rel'] = get_rel(get_pct(player['fenwick_a'] - player['shots_a'], player['fenwick_a']), miss_pct_off)

    # Delete a bunch of shit
    del player['goals_f']
    del player['shots_f']
    del player['fenwick_f']
    del player['corsi_f']
    del player['goals_a']
    del player['shots_a']
    del player['fenwick_a']
    del player['corsi_a']
    del player['goals_f_off']
    del player['shots_f_off']
    del player['fenwick_f_off']
    del player['corsi_f_off']
    del player['goals_a_off']
    del player['shots_a_off']
    del player['fenwick_a_off']
    del player['corsi_a_off']

    if 'shots_a_off_raw' in list(player.keys()):
        del player['shots_a_off_raw']
        del player['fenwick_a_off_raw']
        del player['shots_f_off_raw']
        del player['fenwick_f_off_raw']

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

    player['off_zone%'] = get_pct(player['face_off'], player['face_off']+player['face_def']+player['face_neu'])
    player['def_zone%'] = get_pct(player['face_def'], player['face_off'] + player['face_def'] + player['face_neu'])
    player['neu_zone%'] = get_pct(player['face_neu'], player['face_off'] + player['face_def'] + player['face_neu'])

    off_zone_pct_off = get_pct(player['face_off_off'], player['face_off_off']+player['face_def_off']+player['face_neu_off'])
    neu_zone_pct_off = get_pct(player['face_neu_off'], player['face_off_off'] + player['face_def_off'] + player['face_neu_off'])
    def_zone_pct_off = get_pct(player['face_def_off'], player['face_off_off'] + player['face_def_off'] + player['face_neu_off'])

    player['off_zone%_rel'] = get_rel(player['off_zone%'], off_zone_pct_off)
    player['def_zone%_rel'] = get_rel(player['def_zone%'], def_zone_pct_off)
    player['neu_zone%_rel'] = get_rel(player['neu_zone%'], neu_zone_pct_off)

    return player


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


