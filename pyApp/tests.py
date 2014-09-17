from django.test import TestCase
from datetime import date, timedelta

from pyApp.models import Finding, ActionPlan, Auditor
from pychamp import calc


class ModelTestCase(TestCase):

    def setUp(self):
        self.asl = Auditor.objects.create(
            id='asl', name='Emperor Palpatine',
            grc_name='Emperor Palpatine/GRC')
        self.al = Auditor.objects.create(
            id='al', name='Darth Vader',
            grc_name='Darth Vader/GRC')
        self.tl = Auditor.objects.create(
            id='tl1', name='Obi-Wan Kenobi',
            grc_name='Obi-Wan Kenobi/GRC')
        self.auditor = Auditor.objects.create(
            id='aud1', name='Luke Skywalker',
            grc_name='Luke Skywalker/GRC')

        self.finding = Finding.objects.create(
            id='I00000',
            title='Test Finding',
            detail='This is jsut filler text',
            risk='High',
            risk_type='Technology',
            status='Open',
            due_date=date.today() + timedelta(days=30),
            responsible_asl=self.asl,
            responsible_al=self.al,
        )

        self.finding.auditors.add(self.auditor)

        self._map = ActionPlan.objects.create(
            id='A0000',
            finding=self.finding,
            detail='This is a test MAP',
            status='Open',
            due_date=date.today() + timedelta(days=30),
        )

        self._map.reviewers.add(self.auditor)
        self._map.reviewers.add(self.tl)

    def test_finding_properties(self):
        self.assertFalse(self.finding.sustainability)
        self.assertEqual(self.finding.sustainability, 0)

        self.assertFalse(self.finding.msi)
        self.assertEqual(self.finding.msi, 0)

        self.assertFalse(self.finding.consumer_harm)
        self.assertEqual(self.finding.consumer_harm, 0)

        self.assertFalse(self.finding.repeat)
        self.assertEqual(self.finding.repeat, 0)

    def test_finding_aging(self):
        self.assertFalse(self.finding.is_past_due)
        self.assertEqual(self.finding.real_due_date, date.today() + timedelta(days=30))

        self.finding.revised_due_date = date.today() - timedelta(days=1)
        self.assertTrue(self.finding.is_past_due)
        self.assertEqual(self.finding.real_due_date, date.today() - timedelta(days=1))

    def test_finding_owners(self):
        self.assertEqual(self.finding.responsible_asl, self.asl)
        self.assertEqual(self.finding.responsible_al, self.al)

        self.assertEqual(self.finding.auditors.count(), 1)
        self.assertEqual(self.finding.first_responsible_auditor, self.auditor)

    def test_finding_maps(self):
        self.assertEqual(self.finding.maps.count(), 1)
        self.assertEqual(self.finding.maps.get(pk=self._map.id), self._map)

    def test_map_properties(self):
        self.assertFalse(self._map.sustainability)
        self.assertEqual(self._map.sustainability, 0)

    def test_map_status(self):
        self._map.sustainability = 1
        self._map.status = 'Recommend Close'
        self._map.due_date = date(2013, 12, 31)
        self._map.completion_date = date(2013, 12, 20)
        self._map.sustainability_due_date = date(2014, 4, 30)
        self.assertNotEqual(self._map.real_status, 'In Sustainability')
        self._map.sustainability_due_date = date.today() + timedelta(days=1)
        self.assertEqual(self._map.real_status, 'In Sustainability')

    def test_map_aging(self):
        self.assertFalse(self._map.is_past_due)
        self.assertFalse(self._map.in_validation)

        self.assertEquals(self._map.real_status, 'Open')
        self.assertFalse(self._map.in_validation)
        self.assertEqual(self._map.due_date_forecast_count, 30)

        self._map.completion_date = date.today() - timedelta(days=5)
        self._map.status = 'Ready for Review'
        self.assertTrue(self._map.in_validation)
        self.assertEqual(self._map.days_in_review, 5)
        self.assertFalse(self._map.review_is_late)

        self._map.completion_date = date.today() - timedelta(days=31)
        self.assertEqual(self._map.days_in_review, 31)
        self.assertTrue(self._map.review_is_late)

    def test_map_reviewer(self):
        self._map.reviewers.clear()
        self.assertFalse(self._map.reviewers.all())
        self.assertEqual(self._map.current_reviewer(),
                         self.finding.first_responsible_auditor)

        self._map.reviewers.add(self.auditor)
        self.assertEqual(self._map.current_reviewer(), self.auditor)

        self._map.reviewers.add(self.tl)
        self.assertEquals(self._map.current_reviewer(), self.tl)

        self._map.reviewers.clear()
        self._map.reviewers.add(self.tl)
        self._map.reviewers.add(self.auditor)
        self.assertEquals(
            self._map.current_reviewer(
                audit_lead=self.al,
                team_leads=[self.tl]),
            self.tl)

        self._map.reviewers.add(self.al)
        self.assertEquals(
            self._map.current_reviewer(
                audit_lead=self.al,
                team_leads=[self.tl]),
            self.al)

        self._map.status = 'Recommend Close'
        self.assertEqual(self._map.current_reviewer(), self.asl)

    def test_auditor_maps(self):
        ActionPlan.objects.create(
            id='A0001',
            finding=self.finding,
            detail='This is a test MAP',
            status='Open',
            due_date=date.today() + timedelta(days=30),
        )
        ActionPlan.objects.create(
            id='A0002',
            finding=self.finding,
            detail='This is a test MAP',
            status='Open',
            due_date=date.today() + timedelta(days=30),
        )
        ActionPlan.objects.create(
            id='A0003',
            finding=self.finding,
            detail='This is a test MAP',
            status='Open',
            due_date=date.today() + timedelta(days=30),
        )

        self.assertEqual(len(self.auditor.current_maps()), 4)


class ViewTestCase(TestCase):

    def setUp(self):
        self.asl = Auditor.objects.create(
            id='asl', name='Emperor Palpatine',
            grc_name='Emperor Palpatine/GRC')
        self.al = Auditor.objects.create(
            id='al', name='Darth Vader',
            grc_name='Darth Vader/GRC')
        self.auditor = Auditor.objects.create(
            id='aud1', name='Luke Skywalker',
            grc_name='Luke Skywalker/GRC')

        self.finding = Finding.objects.create(
            id='I00000',
            title='Test Finding',
            detail='This is jsut filler text',
            risk='High',
            risk_type='Technology',
            status='Open',
            due_date=date.today() + timedelta(days=30),
            responsible_asl=self.asl,
            responsible_al=self.al,
        )

        self.finding.auditors.add(self.auditor)

        self._map = ActionPlan.objects.create(
            id='A0000',
            finding=self.finding,
            detail='This is a test MAP',
            status='Open',
            due_date=date.today() + timedelta(days=30),
        )

        self._map.reviewers.add(self.auditor)


class CalcTestCase(TestCase):

    def setUp(self):
        a = Auditor.objects.create(
            id='aud1', name='Luke Skywalker',
            grc_name='Luke Skywalker/GRC'
        )
        f = Finding.objects.create(
            id='I00000',
            title='Test Finding',
            detail='This is jsut filler text',
            risk='High',
            risk_type='Technology',
            status='Open',
            due_date=date.today() + timedelta(days=30),
        )
        f.auditors.add(a)

        ActionPlan.objects.create(
            id='Open',
            finding=f,
            detail='This is a test MAP',
            status='Open',
            due_date=date.today() + timedelta(days=30),
        )

        ActionPlan.objects.create(
            id='Late91',
            finding=f,
            detail='This is a test MAP',
            status='Ready for Review',
            due_date=date.today() - timedelta(days=100),
            completion_date=date.today() - timedelta(days=100)
        )

        ActionPlan.objects.create(
            id='Late60_90',
            finding=f,
            detail='This is a test MAP',
            status='Ready for Review',
            due_date=date.today() - timedelta(days=70),
            completion_date=date.today() - timedelta(days=70)
        )

        ActionPlan.objects.create(
            id='Late30_60',
            finding=f,
            detail='This is a test MAP',
            status='Ready for Review',
            due_date=date.today() - timedelta(days=50),
            completion_date=date.today() - timedelta(days=50)
        )

        ActionPlan.objects.create(
            id='InReview',
            finding=f,
            detail='This is a test MAP',
            status='Ready for Review',
            due_date=date.today() - timedelta(days=15),
            completion_date=date.today() - timedelta(days=15)
        )

    def text_my_map(self):
        me = Auditor.objects.get(pk='aud1')

        my_maps = me.current_maps
        table_values = calc.parse_aging_data(my_maps)

        self.assertIsInstance(table_values, list)
        self.assertEqual(table_values[0][0], "91+ Days")
        self.assertEqual(table_values[0][1], 1)
        self.assertEqual(table_values[1][1], 1)
        self.assertEqual(table_values[2][1], 1)
        self.assertEqual(table_values[3][1], 1)
        self.assertEqual(table_values[4][1], 4)
        self.assertEqual(table_values[4][4], 4)