"""
This file contains all the helpers functions used for querying data that are used by more than one view. 
"""
from django.db.models import F
import ast


def filter_strength(data, strength):
    """
    Filter by given strength
    
    :param data: data we have at that point
    :param strength: given strength
    
    :return: query 
    """
    even = ['5x5', '4x4', '3x3']
    pp = ['6x5', '6x4', '6x3', '5x4', '5x3', '4x3']
    pk = ['5x6', '4x6', '3x6', '4x5', '3x5', '3x4']

    # If it's has a 6 they obviously want empty net stuff otherwise don't bother
    # Holds 1 is true, 0 if not
    is_empty = 1 if '6' in strength else 0

    if strength == "PP":
        return data.filter(strength__in=pp).filter(if_empty=is_empty)
    if strength == "PK":
        return data.filter(strength__in=pk).filter(if_empty=is_empty)
    if strength == "Even":
        return data.filter(strength__in=even).filter(if_empty=is_empty)
    if strength != 'All Situations':
        return data.filter(strength=strength).filter(if_empty=is_empty)
    else:
        return data.exclude(strength='0x0')


def filter_players(data, players):
    """
    Filter by players searched
    
    :param data: data we have at that point
    :param players: players specified
    
    :return: query
    """
    # Convert string representation of list to an actual list
    try:
        players = ast.literal_eval(players)
    except (SyntaxError, ValueError) as e:
        players = []

    if players:
        return data.filter(player__in=players)
    else:
        return data


def filter_team(data, team):
    """
    Filter by team selected
    
    :param data: data we have at that point
    :param team: team selected (if any)
    
    :return: query
    """
    if team != '':
        return data.filter(team=team)
    else:
        return data


def filter_toi(data, toi, if_team):
    """
    Filter by toi minimum 
    
    :param data: data we have at that point 
    :param toi: toi threshold 
    :param if_team: If the request is for a team query. This is because for teams its 'toi' but for skaters its 'toi_on'
    
    :return: query
    """
    if toi != 0:
        if if_team:
            return data.filter(toi__gte=convert_to_seconds(toi))
        else:
            return data.filter(toi_on__gte=convert_to_seconds(toi))
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
        return data.filter(game_id__lte=30000)

    if season_type == 'Playoffs':
        return data.filter(game_id__gt=30000)

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
