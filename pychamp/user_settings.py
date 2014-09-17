"""
.. module:: pyChampion.user_settings
    :synopsis: Custom settings for configuring team settings

.. moduleauthor: Alex Nelson <w.alexnelson@gmail.com>

This module contains the needed functions to interact with the pickled
user settings for current user, audit team, and team lead settings.
"""

from django.core.exceptions import ObjectDoesNotExist
from pychamp import pickler
from pyApp.models import Auditor


def _get_user_settings():
    data = pickler.load()

    settings = None
    if data and 'user_settings' in data:
        settings = data['user_settings']

    return settings


def _sub_team():
    data = _get_user_settings()

    team_config = None
    if data and 'sub_team' in data:
        team_config = data['sub_team']

    return team_config


def _audit_team():
    data = _get_user_settings()

    team_config = None
    if data and 'audit_team' in data:
        team_config = data['audit_team']

    return team_config


def current_user():
    data = _get_user_settings()
    if data and 'current_user' in data:
        user_id = data['current_user']

        return Auditor.objects.get(pk=user_id)


def audit_lead():
    data = _audit_team()
    if data and 'audit_lead' in data:
        user_id = _audit_team()['audit_lead']
        return Auditor.objects.get(pk=user_id)


def team_tls():
    team_leads = []
    data = _audit_team()
    if data and 'team_leads' in data:
        for uid in data['team_leads']:
            try:
                team_leads.append(Auditor.objects.get(pk=uid))
            except ObjectDoesNotExist:
                continue

        team_leads.sort(key=lambda x: x.name.lower())
        return team_leads


def team_members():
    members = []
    data = _audit_team()
    if data and 'members' in data:
        for uid in data['members']:
            try:
                members.append(Auditor.objects.get(pk=uid))
            except ObjectDoesNotExist:
                continue

        members.sort(key=lambda x: x.name.lower())
        return members


def team_lead():
    data = _sub_team()
    if data and 'team_lead' in data:
        try:
            user_id = _sub_team()['team_lead']
            return Auditor.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return


def team_lead_members():
    members = []
    data = _sub_team()
    if data and 'members' in data:
        for uid in _sub_team()['members']:
            try:
                members.append(Auditor.objects.get(pk=uid))
            except ObjectDoesNotExist:
                continue

        members.sort(key=lambda x: x.name.lower())
        return members