# project/tests/test_event_reports.py

import datetime
import json

from project.tests.base import BaseTestCase
from project.tests.aux import add_event_type, add_event


now = datetime.datetime.now()


class TestEventServiceReports(BaseTestCase):

    def test_simple_report(self):
        """Ensure get report behaves correctly."""
        et1 = add_event_type("x-ray", 50000)
        et2 = add_event_type("ct", 200000)
        add_event(et1.id, 4)
        add_event(et2.id, 4)
        add_event(et2.id, 5)
        add_event(et2.id, 5)
        add_event(et2.id, 6)

        report = {now.strftime("%Y"): {now.strftime("%b"): {
            '4': {'non-reimbursed SEK': 2500},
            '5': {'non-reimbursed SEK': 4000},
            '6': {'non-reimbursed SEK': 2000}
        }}}

        with self.client:
            response = self.client.get('/events/report')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('generated_at' in data['data'])
            self.assertEqual(report, data['data']['report'])
            self.assertIn('success', data['status'])

    def test_report_filter_caregivers(self):
        """Ensure get report filters caregivers."""
        et1 = add_event_type("x-ray", 50000)
        et2 = add_event_type("ct", 200000)
        add_event(et1.id, 4)
        add_event(et2.id, 4)
        add_event(et2.id, 5)
        add_event(et2.id, 5)
        add_event(et2.id, 6)

        report = {now.strftime("%Y"): {now.strftime("%b"): {
            '4': {'non-reimbursed SEK': 2500},
            '6': {'non-reimbursed SEK': 2000}
        }}}

        with self.client:
            response = self.client.post(
                '/events/report',
                data=json.dumps(dict(
                    caregiver_ids=[4, 6, 7]
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('generated_at' in data['data'])
            self.assertEqual(report, data['data']['report'])
            self.assertIn('success', data['status'])

    def test_report_filter_time(self):
        """Ensure get report filters by time."""
        et1 = add_event_type("x-ray", 50000)
        et2 = add_event_type("ct", 200000)
        add_event(et1.id, 4, start_time='2017-10-28T23:28:23.456701')
        add_event(et2.id, 4, start_time='2016-10-28T23:28:23.456701')
        add_event(et2.id, 5, start_time='2017-10-28T23:28:23.456701')
        add_event(et2.id, 5, start_time='2017-10-28T23:28:23.456701')
        add_event(et2.id, 5, reimbursed=True,
                  start_time='2017-10-28T23:28:23.456701')
        add_event(et2.id, 5, start_time='2018-10-28T23:28:23.456701')

        report = {'2017': {'Oct': {
            '4': {'non-reimbursed SEK': 500},
            '5': {'non-reimbursed SEK': 4000, 'reimbursed SEK': 2000}
        }}}

        with self.client:
            response = self.client.post(
                '/events/report',
                data=json.dumps(dict(
                    min_time='2017-09-28T23:28:23.456701',
                    max_time='2017-11-28T23:28:23.456701'
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('generated_at' in data['data'])
            self.assertEqual(report, data['data']['report'])
            self.assertIn('success', data['status'])

    def test_report_wrong_filter(self):
        """Ensure get report fails when filter inputs are wrong."""
        with self.client:
            response = self.client.post(
                '/events/report',
                data=json.dumps(dict(
                    min_time='invalid data',
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('fail', data['status'])
