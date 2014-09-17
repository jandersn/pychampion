# -*- coding: utf-8 -*-

"""
.. module:: PyChampion.excel
    :platform: Windows
    :synopsis: Manipulate Excel source files into data for writing to 
        the database

.. moduleauthor: Alex Nelson <w.alexnelson@gmail.com>

This module contains the needed functions to manipulate an Excel-base
FindingTrack report into alchemy objects for writing to the database

.. note:: Global variables are based on the Ad Hoc reporting. If headers 
    ever change then these will need to be updated

Attributes:
    FINDING_REPORT_HEADERS (dict): Global Variables used to parse required 
        fields out of an excel spreadsheet for a :py:class:`.Finding` 
        object.
    MAP_REPORT_HEADERS (dict): Global Variables used to parse required 
        fields out of an excel spreadsheet for a :py:class:`.Map` object. 
    AUDITOR_REPORT_HEADERS (dict): Global Variables used to parse required 
        fields out of an excel spreadsheet for a :py:class:`.Auditor` 
        object. 
    REVIEW_REPORT_HEADERS (dict): Global Variables used to parse required 
        fields out of an excel spreadsheet for a :py:class:`.Review` object. 
    VERSION_REPORT_HEADERS (dict): Global Variables used to parse required 
        fields out of an excel spreadsheet for a :py:class:`.Version` object. 

"""

import os
from datetime import date

FINDING_REPORT_HEADERS = dict(id='Point Sheet / Finding - Document Identifier',
                              audit_number='Point Sheet / Finding - Audit Number',
                              audit_name='Point Sheet / Finding - Audit Title',
                              status='Point Sheet / Finding - Status',
                              closed_date='Point Sheet / Finding - Closed Date',
                              repeat='Point Sheet / Finding - Repeat Point Sheet / Finding',
                              risk='Point Sheet / Finding - Finding Risk Level',
                              title='Point Sheet / Finding - Point Sheet / FindingTitle',
                              sustainability_due_date="Point Sheet / Finding - Projected end date of sustainability testing",
                              revised_due_date='Point Sheet / Finding - Finding Revised Due Date',
                              detail='Point Sheet / Finding - Point Sheet / Finding Details',
                              risk_type='Point Sheet / Finding - Related Risk Type',
                              sustainability='Point Sheet / Finding - Sustainability Testing',
                              completion_date='Point Sheet / Finding - Finding Actual Completion Date',
                              owner_bu='Point Sheet / Finding - Finding Owner Business Unit',
                              auditor='Point Sheet / Finding - Responsible Auditors (Delimited)',
                              msi='Point Sheet / Finding - Management Self Identified',
                              responsible_al='Point Sheet / Finding - Responsible AL',
                              owner='Point Sheet / Finding - Finding Owner',
                              consumer_harm='Point Sheet / Finding - Consumer Harm',
                              due_date='Point Sheet / Finding - Original Due Date',
                              responsible_asl='Point Sheet / Finding - Responsible ASL')

MAP_REPORT_HEADERS = dict(id='Management Action Plan - Document Identifier',
                          finding_id='Point Sheet / Finding - Document Identifier',
                          detail="Management Action Plan - Management Action Plan (MAP) Details",
                          reviewer="Management Action Plan - Management Action Plan Reviewer (Delimited)",
                          status="Management Action Plan - Status",
                          due_date="Management Action Plan - MAP Original Due Date",
                          revised_due_date="Management Action Plan - Revised Due Date",
                          completion_date="Management Action Plan - MAP Completion Date",
                          sustainability="Management Action Plan - Sustainability Testing",
                          sustainability_due_date="Management Action Plan - Projected end date of sustainability testing",
                          owner="Management Action Plan - MAP Respondent / Owner (Delimited)",
                          owner_bu="Management Action Plan - MAP Respondent Business Unit",
                          closed_date="Management Action Plan - Closed Date")

AUDITOR_REPORT_HEADERS = dict(id='ID', name='Name', grc_name='GRC Name',
                              title='Title', team='Team')

REVIEW_REPORT_HEADERS = dict(map_id='MAP ID',
                             reviewer_id='Reviewer ID',
                             date='Review Date',
                             detail='Review Detail',
                             level='Review Level',
                             sustainability="Sustainability Review")

VERSION_REPORT_HEADERS = dict(document='Document', version='Version',
                              version_date='Version Date')


def get_finding_report_path(root_path):
    """Check the Report directory for a single report

    An error will be raised if anything other than a single report is found

    Args:
        root_path (str): Directory that contains the Finding Track pyApp

    Returns:
        str: absolute path of Finding Track report
    """
    files = {}

    # Browse directory for all XLSX or XLS files
    for file_name in os.listdir(root_path):
        if os.path.isfile(os.path.join(root_path, file_name)) and (
                file_name.endswith('.xlsx', len(file_name.lower()) - 5) or
                file_name.endswith('.xls', len(file_name.lower()) - 4)):
            files[file_name] = os.path.join(root_path, file_name)

    if len(files.keys()) != 1:
        raise ValueError("ERROR: Unable to open report at %s. Confirm there is "
                         "only one report in that directory and that it is not "
                         "currently in use" % root_path)
    else:
        return files.items()[0][1]


def read_finding(report, row_index, date_mode, headers):
    """Parses a Finding Track report line item into the necessary
    :py:class:`.Finding` attributes

    Args:
        report (xlrd.sheet): Excel worksheet of Finding Track report
        row_index (int): Row number to parse
        date_mode (xlrd.book.datemode): The datemode of the workbook
        headers (dict of str): Report headers for all Finding related fields

    Returns:
        dict: Dictionary of Finding attributes
        list: (List of Responsible Auditor names, responsible Audit lead name,
            responsible PGA name)
    """
    import xlrd

    values = {}
    auditors = ""
    al = ""
    asl = ""
    for col_index in range(report.ncols):
        col_header = report.cell(0, col_index).value
        for key, header in headers.items():
            if col_header.lower() == header.lower():
                if "date" in header.lower():
                    cell = report.cell(row_index, col_index)
                    if (cell.ctype != xlrd.XL_CELL_BLANK) and (
                            cell.ctype != xlrd.XL_CELL_EMPTY):
                        date_value = xlrd.xldate_as_tuple(cell.value, date_mode)
                        values[key] = date(*date_value[:3])
                    else:
                        values[key] = None
                elif key.lower() == "auditor":
                    auditors = report.cell(row_index, col_index).value.strip()
                elif key.lower() == "responsible_al":
                    al = report.cell(row_index, col_index).value.strip()
                elif key.lower() == "responsible_asl":
                    asl = report.cell(row_index, col_index).value.strip()
                elif key.lower() == 'msi' or key.lower() == 'repeat' \
                        or key.lower() == 'consumer_harm' \
                        or key.lower() == 'sustainability':
                    if report.cell(row_index, col_index).value == "" \
                            or report.cell(row_index,
                                           col_index).value.lower() == "no":
                        values[key] = 0
                    else:
                        values[key] = 1
                else:
                    cell_value = report.cell(row_index, col_index).value
                    if isinstance(cell_value, str):
                        cell_value = cell_value.strip()
                    values[key] = cell_value

    return {'finding_values': values, 'auditors': auditors.split(","),
            'responsible_al': al, 'responsible_asl': asl}


def read_map(report, row_index, date_mode, headers):
    """Parses a Finding Track report line item into the necessary
    :py:class:`.Map` attributes

    Args:
        report (xlrd.sheet): Excel worksheet of Finding Track report
        row_index (int): Row number to parse
        date_mode (xlrd.book.datemode): The datemode of the workbook
        headers (dict of str): Report headers for all Map related fields

    Returns:
        dict: Dictionary of Map attributes
        list of str: Map reviewers
    """
    import xlrd

    values = {}
    reviewers = ''
    for col_index in range(report.ncols):
        col_header = report.cell(0, col_index).value
        for key, header in headers.items():
            if col_header.lower() == header.lower():
                if "date" in header.lower():
                    cell = report.cell(row_index, col_index)
                    if (cell.ctype != xlrd.XL_CELL_BLANK) and (
                            cell.ctype != xlrd.XL_CELL_EMPTY):
                        date_value = xlrd.xldate_as_tuple(cell.value, date_mode)
                        values[key] = date(*date_value[:3])
                    else:
                        values[key] = None
                elif key.lower() == 'sustainability':
                    if report.cell(row_index, col_index).value != "":
                        values[key] = 1
                    else:
                        values[key] = 0
                elif "reviewer" in header.lower():
                    reviewers = report.cell(row_index, col_index).value.strip()
                else:
                    values[key] = report.cell(row_index,
                                              col_index).value.strip()

    return {'map_values': values, 'reviewers': reviewers.split(",")}


def read_auditor(report, row_index, headers):
    """Parses a report line item into the necessary :py:class:`.Auditor`
    attributes

    Args:
        report (xlrd.sheet): Excel worksheet of Finding Track report
        row_index (int): Row number to parse
        headers (dict of str): Report headers for all Auditor related fields

    Returns:
        dict: Dictionary of Auditor attributes
    """
    values = {}
    for col_index in range(report.ncols):
        col_header = report.cell(0, col_index).value
        for key, header in headers.items():
            if col_header.lower() == header.lower():
                values[key] = report.cell(row_index, col_index).value.strip()

    return values


def read_review(report, row_index, date_mode, headers):
    """Parses a report line item into the necessary :py:class:`.Review`
    attributes

    Args:
        report (xlrd.sheet): Excel worksheet of Finding Track report
        row_index (int): Row number to parse
        date_mode (xlrd.book.datemode): The datemode of the workbook
        headers (dict of str): Report headers for all Review related fields

    Returns:
        dict: Dictionary of Review attributes
    """
    import xlrd

    values = {}
    for col_index in range(report.ncols):
        col_header = report.cell(0, col_index).value
        for key, header in headers.items():
            if col_header.lower() == header.lower():
                if "date" in header.lower():
                    cell = report.cell(row_index, col_index)
                    if (cell.ctype != xlrd.XL_CELL_BLANK) and (
                            cell.ctype != xlrd.XL_CELL_EMPTY):
                        date_value = xlrd.xldate_as_tuple(cell.value, date_mode)
                        values[key] = date(*date_value[:3])
                    else:
                        values[key] = cell.value
                elif "level" in header.lower() or "sust" in header.lower():
                    values[key] = report.cell(row_index, col_index).value
                else:
                    values[key] = report.cell(row_index,
                                              col_index).value.strip()

    return values


def read_version(report, row_index, date_mode, headers):
    """Parses a report line item into the necessary :py:class:`.Version`
    attributes

    Args:
        report (xlrd.sheet): Excel worksheet of Finding Track report
        row_index (int): Row number to parse
        date_mode (xlrd.book.datemode): The datemode of the workbook
        headers (dict of str): Report headers for all Version related fields

    Returns:
        dict: Dictionary of Version attributes
    """
    import xlrd

    values = {}
    for col_index in range(report.ncols):
        col_header = report.cell(0, col_index).value
        for key, header in headers.items():
            if col_header.lower() == header.lower():
                if "date" in header.lower():
                    cell = report.cell(row_index, col_index)
                    if (cell.ctype != xlrd.XL_CELL_BLANK) and (
                            cell.ctype != xlrd.XL_CELL_EMPTY):
                        date_value = xlrd.xldate_as_tuple(cell.value, date_mode)
                        values[key] = date(*date_value[:3])
                    else:
                        values[key] = cell.value
                else:
                    values[key] = report.cell(row_index,
                                              col_index).value.strip()

    return values


def open_workbook(path):
    """Opens an excel workbook from the provided path

    Args:
        path (str): Path to the excel workbook to open

    Returns:
        xlrd.book: Excel workbook
    """
    try:
        import xlrd

        wb = xlrd.open_workbook(path)
    except:
        raise
    else:
        return wb