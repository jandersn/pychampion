"""
.. module:: pyChampion.ct_processors
    :synopsis: Custom Django Context Processors

.. moduleauthor: Alex Nelson <w.alexnelson@gmail.com>

This module contains the needed functions to display custom variables within
DJango templates without needing to handle them through views.
"""

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from pychamp import pickler, user_settings


def db_refresh_date(request):

    data = pickler.load()

    if data and settings.REFRESH_KEY in data:
        response = data[settings.REFRESH_KEY]
    else:
        response = 'Never'

    return {settings.REFRESH_KEY: response}


def current_user_name(request):

    try:
        user = user_settings.current_user()
        name = user.name
    except ObjectDoesNotExist:
        name = 'Anonymous'
    except Exception as e:
        name = 'Anonymous'
        print e.message
    finally:
        return {'CURRENT_USER_NAME': name}


def finding_track_dir(request):

    return {'FINDING_TRACK_REPORT': settings.FINDING_TRACK_DIR}


def other_report_path(request):

    return {'OTHER_REPORT': settings.OTHER_REPORT_PATH}