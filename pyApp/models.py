"""
.. module:: pyApp.models
    :synopsis: Django ORM layer

.. moduleauthor: Alex Nelson <w.alexnelson@gmail.com>

This module contains the needed class objects to interact with the SQLite
database.
"""

from django.db import models
from django.db.models import Q
from datetime import date, timedelta, datetime


class Auditor(models.Model):
    """Auditor class"""
    id = models.CharField(max_length=20, primary_key=True, unique=True)
    name = models.CharField(blank=False, max_length=250)
    grc_name = models.CharField(blank=False, max_length=250)
    title = models.CharField(max_length=200, blank=True)
    team = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

    def current_maps(self):
        """Return any Map where auditor is listed as a responsible auditor on
        the Finding or a reviewer

        Returns:
            list of :py:class:`.ActionPlan`
        """

        my_maps = []
        # Get all Maps where auditor is the responsible auditor
        [[my_maps.append(m) for m in f.maps.filter(~Q(status='Closed')).all()] for f in self.findings.filter(~Q(status='Closed')).all()]

        # Get all Maps where auditor is listed a reviewer
        [my_maps.append(m) for m in self.maps.filter(~Q(status='Closed')).all()]

        # Make list unique
        my_maps = list(set(my_maps))

        return my_maps


class Finding(models.Model):
    """Finding class

    Examples:
        Creating a new Finding with a dictionary of values::

            from pyApp.models import Finding

            finding_values = {
                'id': 'AI00000',
                'audit_number': '2014-AS-000',
                'audit_name': 'Test Audit',
                'title': 'Test Finding',
                'detail': 'Finding Detail Test',
                'owner': 'Luke Skywalker',
                'owner_bu': 'The Republic',
                'risk': 'High',
                'risk_type': 'Technology',
                'msi': 0, # 0 = False, 1 = True
                'repeat': 0, # 0 = False, 1 = True
                'consumer_harm': 0, # 0 = False, 1 = True
                'status': 'Open',
                'due_date': '2014-05-15',
                'revised_due_date': '', # Can be blank
                'completion_date': '', # Can be blank
                'sustainability': 0, # 0 = False, 1 = True
                'sustainability_due_date': '', # Can be blank
                'closed_date': '', # Can be blank
                'responsible_asl_id': 'portfolio_general_auditor_id',
                'responsible_al_id': 'regional_al_id'
            }

            new_finding = Finding(**finding_values)
    """

    id = models.CharField(max_length=20, primary_key=True, unique=True)
    audit_number = models.CharField(max_length=15, blank=True, null=True)
    audit_name = models.CharField(max_length=200, blank=True, null=True)
    title = models.TextField()
    detail = models.TextField()
    owner = models.CharField(max_length=250, blank=True, null=True)
    owner_bu = models.CharField(max_length=250, blank=True, null=True)
    risk = models.CharField(max_length=25, blank=True, null=True)
    risk_type = models.CharField(max_length=250, blank=True, null=True)
    msi = models.BooleanField(default=0)
    repeat = models.BooleanField(default=0)
    consumer_harm = models.BooleanField(default=0)
    status = models.CharField(blank=True, null=True, max_length=125)
    due_date = models.DateField(blank=True, null=True)
    revised_due_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    sustainability = models.BooleanField(default=0)
    sustainability_due_date = models.DateField(blank=True, null=True)
    closed_date = models.DateField(blank=True, null=True)
    responsible_asl = models.ForeignKey(Auditor, related_name="owning_asl",
                                        null=True, blank=True)
    responsible_al = models.ForeignKey(Auditor, related_name="owning_al",
                                       null=True, blank=True)
    auditors = models.ManyToManyField(Auditor, related_name="findings")

    def __str__(self):
        return "Finding %s: %s, %s" % (self.id, self.status, self.risk)

    @property
    def real_due_date(self):
        """Date the client needs to close the Finding

        FindingTrack allows for Revised Due Dates

        Returns:
            datetime.date
        """
        if self.revised_due_date:
            due_date = self.revised_due_date
        else:
            due_date = self.due_date

        return due_date

    @property
    def is_past_due(self):
        """Should Finding reported as late to the Audit committee

        Returns:
            bool: **True** if :py:attr:`Finding.real_due_date` is greater
                than current date, **False** otherwise
        """

        return self.real_due_date < date.today()

    @property
    def first_responsible_auditor(self):
        """The first listed auditor on a Finding

        Findings potentially could have many responsible auditors

        Return:
            :py:class:`.Auditor`: The first listed auditor from the
                relational database table
        """
        if self.auditors:
            return self.auditors.all()[0]


class ActionPlan(models.Model):
    """

    Examples:
        Creating a new MAP with a dictionary of values::

            from pyApp.models import ActionPlan

            map_values = {
                'id': 'A0000',
                'finding_id', 'AI0000',
                'detail': 'Action Plan Detail Example',
                'status': 'Open',
                'due_date': '2014-05-15',
                'revised_due_date': '', # Can be blank
                'completion_date': '', # Can be blank
                'sustainability': 0, # 0 = False, 1 = True
                'sustainability_due_date': '', # Can be blank
                'closed_date': '', # Can be blank
            }

            new_map = ActionPlan(**map_values)

    """
    id = models.CharField(max_length=20, primary_key=True, null=False,
                          unique=True)
    finding = models.ForeignKey(Finding, related_name="maps")
    detail = models.TextField()
    status = models.CharField(max_length=125, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    revised_due_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    sustainability = models.BooleanField(default=0)
    sustainability_due_date = models.DateField(blank=True, null=True)
    owner = models.CharField(max_length=250, blank=True, null=True)
    owner_bu = models.CharField(max_length=250, blank=True, null=True)
    closed_date = models.DateField(blank=True, null=True)
    reviewers = models.ManyToManyField(Auditor, related_name="maps", blank=True,
                                       null=True)

    def __str__(self):
        return "%s: %s" % (self.id, self.real_status)

    def __eq__(self, other):
        return self.pk == other.pk

    def __hash__(self):
        return (self.id, self.status).__hash__()

    @property
    def in_validation(self):

        validation = False

        if 'review' in self.real_status.lower() or \
                        'recommend' in self.real_status.lower():
            validation = True

        return validation

    @property
    def real_status(self):
        """Interprets the state of sustainability testing into the MAP status

        Returns:
            str: :py:attr:`Map.status` or *In Sustainability*
        """

        status = self.status

        if self.sustainability and self.sustainability_due_date and \
                        self.sustainability_due_date > date.today():
            status = "In Sustainability"

        return status

    @property
    def real_due_date(self):
        """Returns the date the client needs to close the Map

        Finding Track allows for revised due dates

        Returns:
            datetime.date
        """
        if self.sustainability_due_date:
            actual_due_date = self.sustainability_due_date
        elif self.revised_due_date:
            actual_due_date = self.revised_due_date
        else:
            actual_due_date = self.due_date

        return actual_due_date

    def current_reviewer(self, audit_lead=None, team_leads=None):
        """Returns the current reviewer of the MAP

        Keyword Args:
            audit_lead (Auditor): The known audit lead for the audit
                team
            team_leads (list of Auditor): The list of team leaders for
                the audit team

        Returns:
            :py:class:`.Auditor`: Best estimate of the current reviewer
                between responsible auditor, team leader, audit leader,
                or portfolio general auditor

        Note:
            As Finding Track's workflow is not a true workflow, this is a best
            estimate for determining who is the current reviewer of a MAP.

            Best practices is to limit the number of reviewers to the
            responsible auditor, the team leader, and the the audit leader
            as the MAP progresses through the *workflow*

            This estimate becomes more accurate as you provide the known
            management team for your audit team, including all the team leads
            and the audit lead.

        Examples:
            **Example 1**: No reviewers are set on the Map yet::

                >>>new_map = ActionPlan(**map_values)
                >>>aud = Auditor(name="Finding Responsible Auditor")
                >>>new_map.finding.responsible_auditors.append(aud)
                >>>new_map.reviewers = []
                >>>print new_map.current_reviewer().name
                Finding Responsible Auditor

            **Example 2**: Multiple reviewers are set on a MAP but audit team
            management not provided. The last added auditor will be considered
            the reviewer. This isn't ideal if the team leader wasn't the last
            provided::

                >>>new_map.reviewers.append(Auditor(name="R2D2"))
                >>>new_map.reviewers.append(Auditor(name="Team Leader Bravo"))
                >>>new_map.reviewers.append(Auditor(name="Luke Skywalker"))
                >>>print new_map.current_reviewer().name
                Luke Skywalker

            **Example 3**: Multiple reviewers are set on a MAP, but audit team
            is known. Providing the audit team results in more accurate
            estimation of the current reviewer::

                >>>tls = [Auditor(name="Team Leader Alpha"),
                ...       Auditor(name="Team Leader Bravo")]
                >>>al = Auditor(name="Han Solo")
                >>>new_map.reviewers.append(Auditor(name="R2D2"))
                >>>new_map.reviewers.append(Auditor(name="Team Leader Bravo"))
                >>>new_map.reviewers.append(Auditor(name="Luke Skywalker"))
                >>>print new_map.current_reviewer(al, tls).name
                Team Leader Bravo

            **Example 4**: Map has been moved to status ``Recommend Close``::

                >>>new_map.finding.responsible_asl = Auditor(name="Darth Vader")
                >>>new_map.status = "Recommend Close"
                >>>print new_map.current_reviewer().name
                Darth Vader
        """
        current_reviewer = None

        if "recommend" in self.real_status.lower():
            current_reviewer = self.finding.responsible_asl

        elif not self.reviewers.all() and self.finding.auditors.all():
            current_reviewer = self.finding.first_responsible_auditor

        elif audit_lead and isinstance(audit_lead, Auditor) and \
                        audit_lead in self.reviewers.all():
            current_reviewer = audit_lead

        elif team_leads and [isinstance(tl, Auditor) for tl in team_leads if
                             tl in self.reviewers.all()]:
            tl = [tl for tl in team_leads if tl in self.reviewers.all()]
            current_reviewer = tl[0]

        elif self.reviewers.all():
            current_reviewer = self.reviewers.all()[self.reviewers.count() - 1]

        return current_reviewer

    @property
    def is_past_due(self):
        """Map is Open and the due date is past

        Returns:
            bool
        """

        return self.real_due_date < date.today() \
            and self.status.lower() == "open"

    @property
    def due_date_forecast_count(self):
        """Returns the number of days from the current date until the MAP is
        due from the client

        Returns:
            int
        """
        if self.is_past_due:
            return -1
        elif self.status.lower() == "open":
            delta = self.real_due_date - date.today()
            return delta.days

    @property
    def review_start_date(self):
        """The date the IAG review should have started based on due dates /
        completion dates

        Returns:
            datetime.date
        """
        if self.sustainability_due_date:
            due_date = self.sustainability_due_date
        elif self.completion_date:
            due_date = self.completion_date
        else:
            due_date = self.real_due_date

        return due_date

    @property
    def review_due_date(self):
        """IAG has 30 days to validate a MAP

        Returns:
            datetime.date
        """
        return self.review_start_date + timedelta(days=30)

    @property
    def review_is_late(self):
        """The MAP has been under review for greater than 30 days

        Returns:
            bool
        """
        return self.review_due_date < date.today() and self.in_validation

    @property
    def days_in_review(self):
        """Total days MAP has been with IAG

        The difference between the current date and the review start date if
        the MAP is Ready for Review or Recommend close

        Returns:
            int
        """
        days = 0

        if self.in_validation and date.today() >= self.review_start_date:
            delta = date.today() - self.review_start_date
            days = delta.days

        return days