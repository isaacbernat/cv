# project/tests/test_events.py


import datetime
import json

from project import db
from project.tests.base import BaseTestCase
from project.tests.aux import add_event_type, add_event


class TestEventService(BaseTestCase):

    def test_ping(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_event(self):
        """Ensure a new event can be added to the database."""
        et = add_event_type("x-ray", 500)
        with self.client:
            response = self.client.post(
                '/events',
                data=json.dumps(dict(
                    type_id=et.id,
                    caregiver_id=2,
                    start_time=datetime.datetime.now().isoformat(),
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])
            response = self.client.get(f'/events/{data["id"]}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertEqual(et.id, data['data']['type_id'])
            self.assertEqual(2, data['data']['caregiver_id'])
            self.assertEqual(False, data['data']['reimbursed'])
            self.assertIn('success', data['status'])

    def test_add_event_always_not_imbursed(self):
        """Ensure new events can be not added as already reimbursed."""
        et = add_event_type("x-ray", 500)
        with self.client:
            response = self.client.post(
                '/events',
                data=json.dumps(dict(
                    type_id=et.id,
                    caregiver_id=2,
                    start_time=datetime.datetime.now().isoformat(),
                    reimbursed=True,
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])
            response = self.client.get(f'/events/{data["id"]}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(False, data['data']['reimbursed'])
            self.assertIn('success', data['status'])

    def test_add_event_ignores_id(self):
        """Ensure new events can be not added with arbitrary id."""
        et = add_event_type("x-ray", 500)
        with self.client:
            response = self.client.post(
                '/events',
                data=json.dumps(dict(
                    id=1337,
                    type_id=et.id,
                    caregiver_id=2,
                    start_time=datetime.datetime.now().isoformat(),
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])
            self.assertEqual(1, data['id'])  # that is, not 1337

    def test_add_event_invalid_type_id(self):
        """Ensure error is thrown if type id is invalid exist."""
        with self.client:
            response = self.client.post(
                '/events',
                data=json.dumps(dict(
                    type_id=5,
                    caregiver_id=2,
                    start_time=datetime.datetime.now().isoformat()
                )),
                content_type='application/json',
            )

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_event_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        with self.client:
            response = self.client.post(
                '/events',
                data=json.dumps(dict()),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_event_missing_json_keys(self):
        """
        Ensure error is thrown if the JSON object lacks any required key.
        """
        et = add_event_type("x-ray", 500)
        with self.client:
            response = self.client.post(
                '/events',
                data=json.dumps(dict(
                    type_id=et.id,
                    start_time=datetime.datetime.now().isoformat()
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

            response = self.client.post(
                '/events',
                data=json.dumps(dict(
                    caregiver_id=5
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_event_with_wrong_date(self):
        """Ensure error is thrown when start_time is not valid."""
        et = add_event_type("x-ray", 500)
        with self.client:
            response = self.client.post(
                '/events',
                data=json.dumps(dict(
                    type_id=et.id,
                    caregiver_id=2,
                    start_time="fail"
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_event(self):
        """Ensure get single event behaves correctly."""
        et = add_event_type("x-ray", 500)
        event = add_event(et.id, 5)

        with self.client:
            response = self.client.get(f'/events/{event.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertEqual(et.id, data['data']['type_id'])
            self.assertEqual(5, data['data']['caregiver_id'])
            self.assertEqual(False, data['data']['reimbursed'])
            self.assertIn('success', data['status'])

    def test_single_event_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/events/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Event does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_event_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/events/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Event does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_events(self):
        """Ensure get all events behaves correctly."""
        et1 = add_event_type("x-ray", 500)
        et2 = add_event_type("ct", 2000)
        add_event(et1.id, 5)
        add_event(et1.id, 4)
        add_event(et2.id, 5, reimbursed=True)
        with self.client:
            response = self.client.get('/events')
            data = json.loads(response.data.decode())
            self.assertIn('success', data['status'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['events']), 3)

            self.assertTrue('created_at' in data['data']['events'][0])
            self.assertEqual(et1.id, data['data']['events'][0]['type_id'])
            self.assertEqual(5, data['data']['events'][0]['caregiver_id'])
            self.assertEqual(False, data['data']['events'][0]['reimbursed'])

            self.assertTrue('created_at' in data['data']['events'][1])
            self.assertEqual(et1.id, data['data']['events'][1]['type_id'])
            self.assertEqual(4, data['data']['events'][1]['caregiver_id'])
            self.assertEqual(False, data['data']['events'][1]['reimbursed'])

            self.assertTrue('created_at' in data['data']['events'][2])
            self.assertEqual(et2.id, data['data']['events'][2]['type_id'])
            self.assertEqual(5, data['data']['events'][2]['caregiver_id'])
            self.assertEqual(True, data['data']['events'][2]['reimbursed'])

    def test_delete_event(self):
        """Ensure deletion of event behaves correctly."""
        et = add_event_type("x-ray", 500)
        event = add_event(et.id, 5)

        with self.client:
            response = self.client.get(f'/events/{event.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])

            response = self.client.delete(f'/events/{event.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Event deleted', data['message'])
            self.assertIn('success', data['status'])

            response = self.client.get(f'/events/{event.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Event does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_delete_missing_event(self):
        """Ensure deletion fails when no event exists."""
        with self.client:
            response = self.client.delete(f'/events/1')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Event does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_reimburse_event(self):
        """Ensure reimbursion of event behaves correctly."""
        et = add_event_type("x-ray", 500)
        event = add_event(et.id, 5)

        with self.client:
            response = self.client.get(f'/events/{event.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(False, data['data']['reimbursed'])
            self.assertIn('success', data['status'])

            response = self.client.post(f'/events/{event.id}/reimburse')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Event reimbursed', data['message'])
            self.assertIn('success', data['status'])

            response = self.client.get(f'/events/{event.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(True, data['data']['reimbursed'])
            self.assertIn('success', data['status'])

    def test_reimburse_missing_event(self):
        """Ensure reimbursion fails when no event exists."""
        with self.client:
            response = self.client.post(f'/events/5/reimburse')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Event does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_reimburse_reimbursed_event(self):
        """Ensure reimbursion fails when event is already reimbursed."""
        et = add_event_type("x-ray", 500)
        event = add_event(et.id, 5, reimbursed=True)

        with self.client:
            response = self.client.get(f'/events/{event.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(True, data['data']['reimbursed'])
            self.assertIn('success', data['status'])

            response = self.client.post(f'/events/{event.id}/reimburse')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Event already reimbursed', data['message'])
            self.assertIn('fail', data['status'])
