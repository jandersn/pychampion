"""
.. module:: pyApp.Views
    :synopsis: Django Views for displaying content to HTML

.. moduleauthor: Alex Nelson <w.alexnelson@gmail.com>

This module contains the needed views to prepare data for display on Django
HTML templates
"""


from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.core import serializers
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from datetime import date, datetime
import json

from pyApp.models import Auditor, ActionPlan, Finding
from pychamp import pickler, user_settings, calc, tasks


def index(request):
    """Display the main page"""
    return render_to_response(
        'index.html',
        context_instance=RequestContext(request)
    )


def search(request):
    """Display the search page"""

    if request.POST:
        kwargs = {}

        if request.POST['audit'] != '':
            kwargs['finding__audit_name__icontains'] = request.POST['audit']
        if request.POST['audit_number'] != '':
            kwargs['finding__audit_number__icontains'] = request.POST['audit_number']
        if request.POST['auditor'] != '':
            kwargs['finding__auditors__name__icontains'] = request.POST['auditor']
        if request.POST['reviewer'] != '':
            kwargs['reviewers__name__icontains'] = request.POST['reviewer']
        if request.POST['owner'] != '':
            kwargs['finding__owner__icontains'] = request.POST['owner']
        if request.POST['respondent'] != '':
            kwargs['owner__icontains'] = request.POST['respondent']
        if request.POST['risk'].lower() != 'select risk...':
            kwargs['finding__risk__icontains'] = request.POST['risk']
        if request.POST['risk-type'] != '':
            kwargs['finding__risk_type__icontains'] = request.POST['risk-type']
        if request.POST['status'].lower() != 'select status...':
            kwargs['finding__status__icontains'] = request.POST['status']
        if request.POST['due-date'] != '':
            due_date = datetime.strptime(request.POST['due-date'], '%Y-%m-%d')
            if request.POST['due-date-param'].lower() == "equals":
                kwargs['due_date'] = due_date
            elif request.POST['due-date-param'].lower() == "before":
                kwargs['due_date__lt'] = due_date
            else:
                kwargs['due_date__gt'] = due_date
        if request.POST['closed-date'] != '':
            closed_date = datetime.strptime(request.POST['closed-date'], '%Y-%m-%d')
            if request.POST['closed-date-param'].lower() == "equals":
                kwargs['closed_date'] = closed_date
            elif request.POST['closed-date-param'].lower() == "before":
                kwargs['closed_date__lt'] = closed_date
            else:
                kwargs['closed_date__gt'] = closed_date

        results = ActionPlan.objects.filter(**kwargs)

        if request.POST['bu'] != '':
            results = results.filter(Q(owner_bu__icontains=request.POST['bu']) | Q(finding__owner_bu__icontains=request.POST['bu']))

        if request.POST['keyword'] != '':
            results = results.filter(Q(detail__icontains=request.POST['keyword']) | Q(finding__detail__icontains=request.POST['keyword']))

        return render_to_response('search.html', {'results': results}, RequestContext(request))
    else:
        return render_to_response(
            'search.html',
            context_instance=RequestContext(request)
        )
@ensure_csrf_cookie
def refresh_db(request):
    """ A view to start a background job and redirect to the status page """
    return render_to_response('refresh_db.html', RequestContext(request))


def settings(request):
    """Display the user settings"""

    data = {}

    try:
        data['current_user'] = user_settings.current_user()
    except ObjectDoesNotExist:
        data['current_user'] = None

    try:
        data['audit_lead'] = user_settings.audit_lead()
    except ObjectDoesNotExist:
        data['audit_lead'] = None

    try:
        data['team_leads'] = user_settings.team_tls()
    except ObjectDoesNotExist:
        data['team_leads'] = None

    try:
        data['team_members'] = user_settings.team_members()
    except ObjectDoesNotExist:
        data['team_members'] = None

    try:
        data['sub_team_lead'] = user_settings.team_lead()
    except ObjectDoesNotExist:
        data['sub_team_lead'] = None

    try:
        data['sub_team_members'] = user_settings.team_lead_members()
    except ObjectDoesNotExist:
        data['sub_team_members'] = None

    return render_to_response('settings.html', data, RequestContext(request))

@csrf_exempt
def poll_state(request):
    """ A view to report the progress of db refresh to the user """
    try:
        tasks.update_database()
    except Exception as e:
        return HttpResponse(
            json.dumps({"Code": "FAIL", "Message": e.message}),
            mimetype='application/json')
    else:
        return HttpResponse(
            json.dumps({
                "Code": "SUCCESS",
                'Message': 'Database sync was successful'}),
            mimetype='application/json')


@csrf_exempt
def search_users(request):
    """Google like auto fill"""
    result = None
    if 'value' in request.POST:
        query = Auditor.objects.filter(name__contains=request.POST['value'])
        result = serializers.serialize('json', query, fields=('id', 'name'))
    return HttpResponse(result, mimetype='application/json')


@csrf_exempt
def save_settings(request):
    """Pickle user settings"""
    if 'team_setup' in request.POST:
        print 'data found...'
        data = request.POST['team_setup']
        data = json.loads(data)
        pickler.update_pickle_value('user_settings', data)

    return HttpResponse("SUCCESS")


def single_map(request):
    """Display details of a single MAP"""
    map_id = request.GET.get('map')
    m = get_object_or_404(ActionPlan, pk=map_id)
    return render_to_response(
        'single_map.html',
        {'map': m},
        RequestContext(request)
    )


def my_maps(request):
    """Create the report for the configured 'Current User'"""
    try:
        user = user_settings.current_user()
        sub_header = user.name
        user_maps = user.current_maps()

    except (ObjectDoesNotExist, AttributeError):
        return render_to_response('my_maps.html', {
            'report_header': 'My MAP Summary:',
            'sub_header': 'ERROR: No Current User set. '
                          'Configure user settings to enable this report.'},
            RequestContext(request))
    else:
        return render_to_response('my_maps.html', {
            'report_header': 'My MAP Summary:',
            'sub_header': sub_header,
            'aging_data': calc.parse_aging_data(user_maps),
            'status_data': calc.parse_status_data(user_maps),
            'open_data': calc.parse_open_aging_data(user_maps),
            'maps': user_maps},
            RequestContext(request))


def audit_lead(request):
    """View to create the report by the configured audit team or provided
    Finding responsible AL
    """
    al_id = request.GET.get('id')
    name = None

    if al_id and al_id == 'team':
        try:
            al = user_settings.audit_lead()
            name = "%s: Team Settings" % al.name
            team_maps = maps_by_audit_team()
            tls = user_settings.team_tls()
            members = user_settings.team_members()
            reviewer_data = calc.parse_reviewer_data(team_maps, al,
                                                     team_leads=tls,
                                                     members=members)
        except (ObjectDoesNotExist, AttributeError):
            team_maps = maps_by_al()
            reviewer_data = calc.parse_reviewer_data(team_maps)
    else:
        try:
            al = Auditor.objects.get(pk=al_id)
            name = al.name
            team_maps = maps_by_al(al_id=al.id)
            reviewer_data = calc.parse_reviewer_data(team_maps, audit_lead=al)
        except (ObjectDoesNotExist, AttributeError):
            team_maps = maps_by_al()
            reviewer_data = calc.parse_reviewer_data(team_maps)

    al_ids = Finding.objects.values_list('responsible_al', flat=True).distinct()
    al_list = [Auditor.objects.get(pk=a) for a in al_ids if a]

    height = 1 + ((len(reviewer_data[0])) + 1) + \
             ((len(reviewer_data[0]) + 1) * 36)
    chart_height = height - 40
    return render_to_response('audit_lead.html', {
        'report_header': "MAP Summary by Audit Lead",
        'sub_header': name,
        'al_list': al_list,
        'aging_data': calc.parse_aging_data(team_maps),
        'status_data': calc.parse_status_data(team_maps),
        'open_data': calc.parse_open_aging_data(team_maps),
        'reviewer_data': reviewer_data,
        'reviewer_chart_height': [height, chart_height],
        'maps': team_maps},
        RequestContext(request))


def team_lead(request):
    """View to create the report by the configured Team Lead settings"""
    try:
        tl = user_settings.team_lead()
        team_maps = maps_by_team_lead()
        reviewer_data = calc.parse_reviewer_data(team_maps)
        height = 1 + ((len(reviewer_data[0])) + 1) + ((len(reviewer_data[0]) + 1) * 36)
        chart_height = height - 40
    except (ObjectDoesNotExist, AttributeError):
        return render_to_response('team_lead.html', {
            'report_header': 'Team Lead Summary',
            'sub_header': 'ERROR: Team Lead not set. '
                          'Configure your user settings to enable this report.'},
            RequestContext(request))
    else:

        return render_to_response('team_lead.html', {
            'report_header': 'Team Lead Summary',
            'sub_header': tl.name,
            'aging_data': calc.parse_aging_data(team_maps),
            'status_data': calc.parse_status_data(team_maps),
            'open_data': calc.parse_open_aging_data(team_maps),
            'reviewer_data': reviewer_data,
            'reviewer_chart_height': [height, chart_height],
            'maps': team_maps},
            RequestContext(request))


def business_unit(request):
    """View to create the report by MAP Owner Business Unit"""
    unit = request.GET.get('unit')
    year = date.today().year - 2
    query_date = date(year=year, month=1, day=1)

    total_maps = ActionPlan.objects.filter(closed_date__gte=query_date)

    if unit:
        team_maps = ActionPlan.objects.filter(~Q(status='Closed'), owner_bu=unit)
    else:
        unit = 'None'
        team_maps = ActionPlan.objects.filter(~Q(status='Closed'), owner_bu='')

    bu_list = ActionPlan.objects.values_list('owner_bu', flat=True).distinct().exclude(owner_bu='')
    if team_maps:
        reviewer_data = calc.parse_audit_lead_data(team_maps)
        height = 1 + ((len(reviewer_data[0])) + 1) + ((len(reviewer_data[0]) + 1) * 36)
        chart_height = height - 40
    else:
        reviewer_data = None
        height = 5
        chart_height = 3

    return render_to_response('bu_report.html', {
        'report_header': "Summary by MAP Owner Business Unit: ",
        'sub_header': unit,
        'aging_data': calc.parse_aging_data(team_maps),
        'status_data': calc.parse_status_data(team_maps),
        'open_data': calc.parse_open_aging_data(team_maps),
        'reviewer_data': reviewer_data,
        'reviewer_chart_height': [height, chart_height],
        'bu_list': bu_list,
        'maps': team_maps,
        'ytd_data': calc.parse_ytd_by_bu(total_maps, bu_list)},
        RequestContext(request))


def risk_type(request):
    """View to create the Report by Finding Risk Type"""
    risk = request.GET.get('type')
    year = date.today().year - 2
    query_date = date(year=year, month=1, day=1)
    total_maps = ActionPlan.objects.filter(closed_date__gte=query_date)
    if risk:
        team_maps = ActionPlan.objects.filter(~Q(status='Closed'), finding__risk_type=risk)
    else:
        risk = 'None'
        team_maps = ActionPlan.objects.filter(~Q(status='Closed'), finding__risk_type='')

    risk_list = ActionPlan.objects.values_list('finding__risk_type', flat=True).distinct().exclude(finding__risk_type='')

    if team_maps:
        reviewer_data = calc.parse_audit_lead_data(team_maps)
        height = 1 + ((len(reviewer_data[0])) + 1) + ((len(reviewer_data[0]) + 1) * 36)
        chart_height = height - 40
    else:
        reviewer_data = None
        height = 5
        chart_height = 3

    return render_to_response('risk_report.html', {
        'report_header': "Summary by Risk Type: ",
        'sub_header': risk,
        'aging_data': calc.parse_aging_data(team_maps),
        'status_data': calc.parse_status_data(team_maps),
        'open_data': calc.parse_open_aging_data(team_maps),
        'reviewer_data': reviewer_data,
        'reviewer_chart_height': [height, chart_height],
        'risk_list': risk_list,
        'ytd_data': calc.parse_ytd_by_risk_type(total_maps, risk_list),
        'maps': team_maps},
        RequestContext(request))


def maps_by_al(al_id=None):

    if al_id:
        maps = ActionPlan.objects.filter(~Q(status='Closed'),
                                         finding__responsible_al__id=al_id)
    else:
        maps = ActionPlan.objects.filter(~Q(status='Closed'),
                                         finding__responsible_al__isnull=True)
    return maps


def maps_by_audit_team():

    al = user_settings.audit_lead()
    tls = user_settings.team_tls()
    members = user_settings.team_members()

    maps = []
    [maps.append(m) for m in al.current_maps()]
    [[maps.append(m) for m in tl.current_maps()] for tl in tls]
    [[maps.append(m) for m in tm.current_maps()] for tm in members]
    maps = list(set(maps))

    return maps


def maps_by_team_lead():

    tl = user_settings.team_lead()
    members = user_settings.team_lead_members()

    maps = []
    [maps.append(m) for m in tl.current_maps()]
    [[maps.append(m) for m in tm.current_maps()] for tm in members]

    maps = list(set(maps))
    return maps