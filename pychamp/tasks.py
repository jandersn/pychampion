"""
.. module:: pyChampion.tasks
    :synopsis: Functions for update database

.. moduleauthor: Alex Nelson <w.alexnelson@gmail.com>

This module contains the needed functions to update the database using
celery asynchronous task scheduling
"""

from datetime import datetime
import time
import os

import django.core.exceptions as django_err
import django.db as django_db
from django.conf import settings

from pychamp import pickler
from pyApp.models import Finding, ActionPlan, Auditor
import pychamp.excel as xl


def update_database():
    """Main Task. Update all tables"""
    # Update Non Finding Track Tables
    try:
        wb = xl.open_workbook(settings.OTHER_REPORT_PATH)
        aud_report = wb.sheet_by_name('Auditor')
    except Exception as e:
        raise e

    for row_index in range(1, aud_report.nrows):

        auditor_values = xl.read_auditor(aud_report, row_index,
                                         xl.AUDITOR_REPORT_HEADERS)
        build_auditor(auditor_values)

    # Update Finding Track Tables
    try:
        full_path = xl.get_finding_report_path(settings.FINDING_TRACK_DIR)
        wb = xl.open_workbook(full_path)
        report = wb.sheet_by_index(0)
    except Exception as e:
        raise e

    else:
        start_row = 1
        existing_count = ActionPlan.objects.all().count()
        #if existing_count > 0:
        #   # Only scan last 500 MAPs + any new MAPs since last scan
        #    start_row = (existing_count - 500) + (report.nrows - existing_count)

        for row_index in range(start_row, report.nrows):

            # Finding Table
            f_values = xl.read_finding(
                report=report,
                row_index=row_index,
                date_mode=wb.datemode,
                headers=xl.FINDING_REPORT_HEADERS
            )

            build_finding(f_values['finding_values'], f_values['responsible_al'],
                          f_values['responsible_asl'], f_values['auditors'])

            # ActionPlan table
            map_values = xl.read_map(report, row_index, wb.datemode,
                                     xl.MAP_REPORT_HEADERS)

            build_action_plan(map_values['map_values'], map_values['reviewers'])

        ctime = time.ctime(os.path.getctime(full_path))
        refresh_date = datetime.strptime(ctime, "%a %b %d %H:%M:%S %Y").date()
        pickler.update_pickle_value(settings.REFRESH_KEY, refresh_date)


def build_auditor(values):
    """Build the auditor from provided values"""
    
    print "... reading auditor %s" % values['name']
    try:
        auditor, created = Auditor.objects.get_or_create(**values)
    except django_db.IntegrityError:
        auditor = Auditor.objects.filter(pk=values['id']).update(**values)
    except django_err.ValidationError as e:
        print e.message, values
    else:
        auditor.save()
     
        
def build_finding(values, al_name, asl_name, auditors):
    """Build a new Finding from provided values, al, asl, and auditors"""

    print "... reading finding %s" % values['id']
    
    # Query for Audit Lead
    try:
        if al_name or al_name != "":
            al = Auditor.objects.get(grc_name=al_name)
            values['responsible_al'] = al
    except Auditor.DoesNotExist:
        print "---- Error: AL %s doesn't exist" % al_name

    # Query for PGA / ASL
    try:
        if asl_name or asl_name != "":
            asl = Auditor.objects.get(grc_name=asl_name)
            values['responsible_asl'] = asl
    except Auditor.DoesNotExist:
        print "---- Error: ASL %s doesn't exist" % asl_name

    # Create & Save Finding
    try:
        kwargs = dict((key, value) for (key, value) in values.iteritems() if key != 'id')
        finding = Finding(pk=values['id'], **kwargs)
    except django_err.ValidationError as e:
        print e.message, values
    else:
        finding.auditors.clear()
        finding.save()
        # Add Responsible Auditors
        for auditor in auditors:
            try:
                a = Auditor.objects.get(grc_name=auditor.strip())
                finding.auditors.add(a)
            except Auditor.DoesNotExist:
                print "---- Error: responsible auditor %s doesn't exist" % auditor.strip()
                pass  # no further work needed    


def build_action_plan(values, reviewers):
    """Build a new ActionPlan from provided values and reviewers"""
    print "... reading map %s" % values['id']
    # try:
    #     finding = Finding.objects.get(pk=values['finding_id'])
    #     values['finding_id'] = finding
    # except Finding.DoesNotExist:
    #     print "---- Error: orphaned map, disgarding"
    #     return

    # kwargs = dict((key, value) for (key, value) in values.iteritems())
    # kwargs = dict((key, value) for (key, value) in values.iteritems() if key != 'finding_id')

    try:
        kwargs = dict((key, value) for (key, value) in values.iteritems() if key != 'id')
        actionplan = ActionPlan(pk=values['id'], **kwargs)
    except django_err.ValidationError as e:
        print e.message, values
    else:

        actionplan.reviewers.clear()
        actionplan.save()

        if reviewers:
            for reviewer in reviewers:
                try:
                    a = Auditor.objects.get(grc_name=reviewer.strip())
                    actionplan.reviewers.add(a)
                except Auditor.DoesNotExist:
                    print "---- Error: reviewer %s doesn't exist" % reviewer.strip()
                    pass  # no further work needed

