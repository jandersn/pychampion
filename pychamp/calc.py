"""
.. module:: pyChampion.calc
    :synopsis: Functions for summarizing MAP details

.. moduleauthor: Alex Nelson <w.alexnelson@gmail.com>

This module contains the needed class objects and functions to create
action plan summary lists, used for populating reprot tables and charts.
"""

from datetime import date


def parse_aging_data(maps):
    """Parse the MAP data for the review aging of the provided maps

    Args:
        maps (list of :py:class:`.ActionPlan`): Sort through maps to determine
         the review aging counts

    The resulting list will fit the following format


    +=====================+=============+===========+=======+===========+
    | 91+ Days            |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | 61-90 Days          |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | 31-60 Days          |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | 0-30 Days           |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | Total               |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+

    """

    row_data = [
        ["91+ Days", 0, 0, 0, 0],
        ["61-90 Days", 0, 0, 0, 0],
        ["31-60 Days", 0, 0, 0, 0],
        ["0-30 Days", 0, 0, 0, 0],
        ["Total", 0, 0, 0, 0]]

    for m in maps:
        if m.in_validation:
            for col, risk in enumerate(["Header", "High", "Medium", "Low", "Total"]):
                if m.finding.risk.lower() == risk.lower():
                    row_data[4][col] += 1
                    row_data[4][4] += 1
                    # 90+
                    if m.days_in_review > 90:
                        row_data[0][col] += 1
                        row_data[0][4] += 1
                    # 61-90
                    elif 90 >= m.days_in_review > 60:
                        row_data[1][col] += 1
                        row_data[1][4] += 1
                    # 31-60
                    elif 60 >= m.days_in_review > 30:
                        row_data[2][col] += 1
                        row_data[2][4] += 1
                    # 0-30
                    elif 30 >= m.days_in_review:
                        row_data[3][col] += 1
                        row_data[3][4] += 1

    chart_data = []
    [chart_data.append([row_data[row][0], row_data[row][4]]) for row in range(0, len(row_data) - 1)]

    return [row_data, chart_data]


def parse_status_data(maps):
    """Parse the provided MAPs into a status summary

    Args:
        maps (list of :py:class:`.ActionPlan`): Sort through maps to summarize
            :py:attr:`.ActionPlan.status`

    The table will be filled out to the following format

    +---------------------+-------------+-----------+-------+-----------+
    |                     |     High    |   Medium  |   Low |   Total   |
    +=====================+=============+===========+=======+===========+
    | Recommend Close     |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | In Sustainability   |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | Ready for Review    |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | Open                |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | Total               |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+

    """

    vheaders = ("Recommend Close",
                "In Sustainability",
                "Ready for Review",
                "Open",
                "Total")

    row_data = [
        ["Recommend Close", 0, 0, 0, 0],
        ["In Sustainability", 0, 0, 0, 0],
        ["Ready for Review", 0, 0, 0, 0],
        ["Open", 0, 0, 0, 0],
        ["Total", 0, 0, 0, 0]]

    for m in maps:
        for col, risk in enumerate(["", "High", "Medium", "Low", ""]):
            for row, status in enumerate(vheaders):
                if m.finding.risk.lower() == risk.lower() \
                        and m.real_status.lower() == status.lower():
                    row_data[row][col] += 1
                    row_data[4][col] += 1
                    row_data[row][4] += 1
                    row_data[4][4] += 1

    chart_data = []
    [chart_data.append([row_data[row][0], row_data[row][4]]) for row in range(0, len(row_data) - 1)]

    return [row_data, chart_data]


def parse_open_aging_data(maps):
    """Parse provided maps for summary data of open maps and forecasted
    due dates

    Args:
        maps (list of :py:class:`.ActionPlan`): Sort through open maps to
        forecast

    The table will be filled out to the following format

    +---------------------+-------------+-----------+-------+-----------+
    |                     |     High    |   Medium  |   Low |   Total   |
    +=====================+=============+===========+=======+===========+
    | Past Due            |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | Due in 7 days       |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | Due 8-14 Days       |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | Due 15+ Days        |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+
    | Total               |       0     |     0     |   0   |     0     |
    +---------------------+-------------+-----------+-------+-----------+

    """

    row_data = [
        ["Past Due", 0, 0, 0, 0],
        ["Due in 7 Days", 0, 0, 0, 0],
        ["Due 8-14 Days", 0, 0, 0, 0],
        ["Due 15+", 0, 0, 0, 0],
        ["Total", 0, 0, 0, 0]]

    for m in maps:
        if m.real_status.lower() == "open":
            row_data[4][4] += 1
            for col, risk in enumerate(["", "High", "Medium", "Low", "Total"]):
                if m.finding.risk.lower() == risk.lower():
                    row_data[4][col] += 1
                    if m.is_past_due:
                        row_data[0][col] += 1
                        row_data[0][4] += 1
                    elif m.due_date_forecast_count < 8:
                        row_data[1][col] += 1
                        row_data[1][4] += 1
                    elif 15 > m.due_date_forecast_count >= 8:
                        row_data[2][col] += 1
                        row_data[2][4] += 1
                    elif m.due_date_forecast_count >= 15:
                        row_data[3][col] += 1
                        row_data[3][4] += 1

    chart_data = []
    [chart_data.append([row_data[row][0], row_data[row][4]]) for row in range(0, len(row_data) - 1)]

    return [row_data, chart_data]


def parse_reviewer_data(maps, audit_lead=None, team_leads=None, members=None):
    """Fill the table with summary data of maps by audit team

    Args:
        maps (list of :py:class:`.ActionPlan`): Sort through open maps to
        forecast

    The table will be filled out to the following format

    +-----------------+-------------+------------+-----------------+-------+
    |                 | Late Review | In Review  | Due From Client | Total |
    +=================+=============+============+=================+=======+
    | Total           |      0      |     0      |       0         |   0   |
    +-----------------+-------------+------------+-----------------+-------+
    | General Auditor |      0      |     0      |       0         |   0   |
    +-----------------+-------------+------------+-----------------+-------+
    | Audit Leader    |      0      |     0      |       0         |   0   |
    +-----------------+-------------+------------+-----------------+-------+
    | Team Member     |      0      |     0      |       0         |   0   |
    +-----------------+-------------+------------+-----------------+-------+

    """
    hheaders = ("", "Late Review", "In Review", "Due from Client", "Total")
    row_data = [
        ["PGA or QA Review", 0, 0, 0, 0],
    ]

    # If audit team was provided
    if audit_lead and team_leads and members:

        row_data.append([audit_lead.name, 0, 0, 0, 0])
        [row_data.append([tl.name, 0, 0, 0, 0]) for tl in team_leads]
        [row_data.append([m.name, 0, 0, 0, 0]) for m in members]
        row_data.append(['Total', 0, 0, 0, 0])

    # Fill table based on the best guess for current reviewers
    else:
        sub_rows = []
        for m in maps:
            current_auditor = m.current_reviewer(audit_lead=audit_lead)
            if current_auditor and not 'recommend' in m.real_status.lower():
                sub_rows.append(current_auditor.name)

        sub_rows = list(set(sub_rows))
        sub_rows.sort()

        [row_data.append([name, 0, 0, 0, 0]) for name in sub_rows]
        row_data.append(['Total', 0, 0, 0, 0])

    for m in maps:
        if m.real_status.lower() != 'closed':
            current_reviewer = m.current_reviewer(audit_lead=audit_lead,
                                                  team_leads=team_leads)
            if current_reviewer:
                row_data[len(row_data) - 1][len(hheaders) - 1] += 1
                for row in range(0, len(row_data)):
                    for col, age in enumerate(hheaders):
                        if (row_data[row][0].lower() == current_reviewer.name.lower()) or (row == 0 and m.real_status.lower() == "recommend close"):
                            if age.lower() == 'late review' and m.days_in_review > 30:
                                row_data[row][col] += 1
                                row_data[row][4] += 1
                                row_data[len(row_data) - 1][col] += 1
                            elif age.lower() == 'in review' \
                                    and 30 >= m.days_in_review > 0:
                                row_data[row][col] += 1
                                row_data[row][4] += 1
                                row_data[len(row_data) - 1][col] += 1
                            elif age.lower() == 'due from client' \
                                    and m.days_in_review == 0:
                                row_data[row][col] += 1
                                row_data[row][4] += 1
                                row_data[len(row_data) - 1][col] += 1

    chart_data = []
    [chart_data.append([row_data[row][0], row_data[row][4]]) for row in range(0, len(row_data) - 1)]

    return [row_data, chart_data]


def parse_audit_lead_data(maps):
    """Fill the with summary data of map summary by audit leaders

    Args:
        maps (list of :py:class:`.ActionPlan`): Sort through open maps to forecast

    The table will be filled out to the following format

    +-------+------+---------------+----------+------------+-------+
    |       | Open | Ready for Rev | In Sust. | Rec. Close | Total |
    +=======+======+===============+==========+============+=======+
    | Total |  0   |      0        |    0     |     0      |   0   |
    +-------+------+---------------+----------+------------+-------+
    | AL 1  |  0   |      0        |    0     |     0      |   0   |
    +-------+------+---------------+----------+------------+-------+
    | AL 2  |  0   |      0        |    0     |     0      |   0   |
    +-------+------+---------------+----------+------------+-------+
    | AL 3  |  0   |      0        |    0     |     0      |   0   |
    +-------+------+---------------+----------+------------+-------+
    """
    if maps:
        hheaders = ("", "Open", "Ready for Review", "In Sustainability",
                    "Recommend Close", "Total")
        audit_leads = []
        [audit_leads.append(m.finding.responsible_al.name) for m in maps if
         m.finding.responsible_al]
        audit_leads = sorted(set(audit_leads))
        audit_leads.append('No AL Listed')

        row_data = []
        [row_data.append([al, 0, 0, 0, 0, 0]) for al in audit_leads]
        row_data.append(['Total', 0, 0, 0, 0, 0])

        # Count Maps
        for m in maps:
            for row, lead in enumerate(audit_leads):
                for col, status in enumerate(hheaders):
                    if m.finding.responsible_al \
                        and m.finding.responsible_al.name.lower() == lead.lower() \
                            and status.lower() == m.real_status.lower():
                        row_data[row][col] += 1
                        row_data[len(row_data) - 1][col] += 1
                        row_data[row][len(hheaders) - 1] += 1
                        row_data[len(row_data) - 1][len(hheaders) - 1] += 1
                    elif lead.lower() == "no al listed" \
                        and not m.finding.responsible_al \
                            and m.real_status.lower() == status.lower():
                        row_data[len(row_data) - 2][col] += 1
                        row_data[len(row_data) - 1][col] += 1
                        row_data[len(row_data) - 2][len(hheaders) - 1] += 1
                        row_data[len(row_data) - 1][len(hheaders) - 1] += 1

        chart_data = []
        [chart_data.append([row_data[row][0], row_data[row][5]]) for row in range(0, len(row_data) - 1)]

        return [row_data, chart_data]


def parse_ytd_by_bu(maps, units):
    """Summarize total number of MAPs closed YTD and YTD-1 by Business Units"""

    current_year = date.today().year

    chart_data = [[unit, 0, 0, 0] for unit in units]

    for index, row in enumerate(chart_data):
        bu = row[0]
        for m in maps:
            if m.owner_bu.lower() == bu.lower():
                if m.closed_date.year == current_year:
                    chart_data[index][1] += 1
                elif m.closed_date.year == current_year-1:
                    chart_data[index][2] += 1
                else:
                    chart_data[index][3] += 1

    return chart_data


def parse_ytd_by_risk_type(maps, risks):
    """Summarize total number of MAPs closed YTD and YTD-1 by Risk Type"""
    current_year = date.today().year

    chart_data = [[risk, 0, 0, 0] for risk in risks]

    for index, row in enumerate(chart_data):
        risk = row[0]
        for m in maps:
            if m.finding.risk_type.lower() == risk.lower():
                if m.closed_date.year == current_year:
                    chart_data[index][1] += 1
                elif m.closed_date.year == current_year-1:
                    chart_data[index][2] += 1
                else:
                    chart_data[index][3] += 1

    return chart_data