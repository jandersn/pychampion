"""
.. module:: pyChampion.urls
    :synopsis: Django URLs for calling necessary views

.. moduleauthor: Alex Nelson <w.alexnelson@gmail.com>

Django interprets HTTP URL using Regex to determine which view to call
"""

from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView
from pyApp import views

urlpatterns = patterns('',

    url(r'^$', views.index, name='home'),
    url(r'^search/', views.search, name='search'),
    url(r'^map_detail/$', views.single_map, name="map_detail"),
    url(r'^refresh/$', views.refresh_db, name="refresh_db"),
    url(r'^refresh/poll_state/$', views.poll_state, name="poll_state"),
    url(r'^refresh/redirect/$', RedirectView.as_view(url='/'), name="redirect"),
    url(r'^settings/$', views.settings, name="settings"),
    url(r'^settings/search/$', views.search_users, name='search_users'),
    url(r'^settings/save/$', views.save_settings),
    url(r'^settings/redirect/$', RedirectView.as_view(url='/')),
    url(r'^reports/my_maps$', views.my_maps, name='my_maps'),
    url(r'^reports/audit_lead/$', views.audit_lead, name='audit_lead_report'),
    url(r'^reports/team_lead$', views.team_lead, name='team_lead_report'),
    url(r'^reports/business_unit/$', views.business_unit, name='business_unit_report'),
    url(r'^reports/risk_type/$', views.risk_type, name='risk_type_report'),

)

urlpatterns += staticfiles_urlpatterns()