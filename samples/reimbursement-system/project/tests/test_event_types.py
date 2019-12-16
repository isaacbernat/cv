# project/tests/test_event_types.py


import json

from project import db
from project.tests.base import BaseTestCase
from project.tests.aux import add_event_type, add_event


class TestEventServiceTypes(BaseTestCase):

    def test_add_event_type(self):
        """Ensure a new event type can be added to the database."""
        with self.client:
            response = self.client.post(
                '/events/types',
                data=json.dumps(dict(
                    name="x-ray",
                    amount_in_cents=500,
                    currency="SEK"
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])
            response = self.client.get(f'/events/types/{data["id"]}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual("x-ray", data['data']['name'])
            self.assertEqual(500, data['data']['amount_in_cents'])
            self.assertEqual("SEK", data['data']['currency'])
            self.assertIn('success', data['status'])

    def test_add_event_type_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        with self.client:
            response = self.client.post(
                '/events/types',
                data=json.dumps(dict()),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_event_type_invalid_currency(self):
        """Ensure error is thrown if event type has unsupported currency."""
        with self.client:
            response = self.client.post(
                '/events/types',
                data=json.dumps(dict(
                    name="x-ray",
                    amount_in_cents=500,
                    currency="EUR"
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid currency.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_duplicate_event_type(self):
        """Ensure error is thrown if the event_type name already exists."""
        et = add_event_type("x-ray", 500)
        with self.client:
            response = self.client.post(
                '/events/types',
                data=json.dumps(dict(
                    name="x-ray",
                    amount_in_cents=500,
                    currency="SEK"
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_event_type_missing_json_keys(self):
        """
        Ensure error is thrown if the JSON object lacks any required key.
        """
        with self.client:
            response = self.client.post(
                '/events/types',
                data=json.dumps(dict(
                    name="x-ray"
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

            response = self.client.post(
                '/events/types',
                data=json.dumps(dict(
                    amount_in_cents=500
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_event_type(self):
        """Ensure get single event type behaves correctly."""
        et = add_event_type("x-ray", 500)

        with self.client:
            response = self.client.get(f'/events/types/{et.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(et.id, data['data']['id'])
            self.assertEqual('x-ray', data['data']['name'])
            self.assertEqual(500, data['data']['amount_in_cents'])
            self.assertEqual('SEK', data['data']['currency'])
            self.assertIn('success', data['status'])

    def test_single_event_type_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/events/types/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Event type does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_event_type_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/events/types/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Event type does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_event_types(self):
        """Ensure get all event types behaves correctly."""
        et1 = add_event_type("x-ray", 500)
        et2 = add_event_type("ct", 2000)
        with self.client:
            response = self.client.get('/events/types')
            data = json.loads(response.data.decode())
            self.assertIn('success', data['status'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['event_types']), 2)

            self.assertEqual(et1.id, data['data']['event_types'][0]['id'])
            self.assertEqual('x-ray', data['data']['event_types'][0]['name'])
            self.assertEqual(
                500, data['data']['event_types'][0]['amount_in_cents'])
            self.assertEqual('SEK', data['data']['event_types'][0]['currency'])

            self.assertEqual(et2.id, data['data']['event_types'][1]['id'])
            self.assertEqual('ct', data['data']['event_types'][1]['name'])
            self.assertEqual(
                2000, data['data']['event_types'][1]['amount_in_cents'])
            self.assertEqual('SEK', data['data']['event_types'][1]['currency'])

    def test_delete_event_type(self):
        """Ensure deletion of event type behaves correctly."""
        et = add_event_type("x-ray", 500)

        with self.client:
            response = self.client.get(f'/events/types/{et.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])

            response = self.client.delete(f'/events/types/{et.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Event type deleted', data['message'])
            self.assertIn('success', data['status'])

            response = self.client.get(f'/events/types/{et.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Event type does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_delete_missing_event_type(self):
        """Ensure deletion fails when no event exists."""
        with self.client:
            response = self.client.delete(f'/events/types/1')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Event type does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_delete_event_type_used_in_event(self):
        """Ensure deletion fails when event type is used in events."""
        with self.client:
            et = add_event_type("x-ray", 500)
            event = add_event(et.id, 5)
            response = self.client.delete(f'/events/types/{et.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Event type is used in existing events.',
                          data['message'])
            self.assertIn('fail', data['status'])
