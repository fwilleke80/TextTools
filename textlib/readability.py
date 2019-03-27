#!/usr/bin/python
# -*- coding: utf-8 -*-


def compute_flesch_reading_ease(asl, asw):
    """Flesch-Reading-Eass Index (DE)
    """
    return 180.0 - asl - (58.5 * asw)

def assess_flesch_reading_ease(fre):
    """Flasch-Reading-Ease Assessment
    Returns an assessment depending on the given fre value.
    """
    if fre < 0.0:
        return 'Invalid FRE index'
    elif fre <= 30.0:
        return 'very difficult'
    elif fre <= 50.0:
        return 'difficult'
    elif fre <= 60.0:
        return 'medium difficult'
    elif fre <= 70.0:
        return 'medium'
    elif fre <= 80.0:
        return 'medium easy'
    elif fre <= 90.0:
        return 'easy'
    elif fre <= 100.0:
        return 'very easy'

def compute_flesch_kincaid_grade_level(asl, asw):
    """Flesch-Kincaid Grade Level (US)
    """
    return (0.39 * asl) + (11.8 * asw) - 15.59

def compute_gunning_fog_index(w, s, d):
    """Gunning-Fog Index (US)
    """
    return ((w / s) + d) * 0.4

def compute_wiener_sachtextformel(MS, SL, IW, ES):
    """Wiener Sachtextformel (DE)
    """
    wstf1 = 0.1935 * MS + 0.1672 * SL + 0.1297 * IW - 0.0327 * ES - 0.875
    wstf2 = 0.2007 * MS + 0.1682 * SL + 0.1373 * IW - 2.779
    wstf3 = 0.2963 * MS + 0.1905 * SL - 1.1144
    wstf4 = 0.2656 * SL + 0.2744 * MS - 1.693
    return (wstf1, wstf2, wstf3, wstf4)
