import unittest
from unittest.mock import MagicMock, patch
from nest_controller import NestController
from scheduler import Scheduler
import json
import time

class TestNestControllerExtended(unittest.TestCase):
    def setUp(self):
        self.config = {
            'issue_token': 'dummy_token',
            'cookies': 'dummy_cookies',
            'user_id': '12345'
        }
        self.controller = NestController(self.config)

    @patch('nest_controller.requests.Session')
    def test_get_status_with_structure(self, mock_session_cls):
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_data = {
            "shared": {
                "serial_1": {
                    "current_temperature": 21.5,
                    "target_temperature": 22.0,
                    "current_humidity": 45,
                    "hvac_mode": "heat",
                    "name": "Living Room"
                }
            },
            "structure": {
                "struct_1": {
                    "name": "My Home",
                    "away": False
                }
            }
        }
        mock_response.json.return_value = mock_data
        self.controller.session = mock_session
        mock_session.get.return_value = mock_response

        result = self.controller.get_status()

        self.assertEqual(len(result['devices']), 1)
        self.assertEqual(result['structure']['structure_id'], 'struct_1')
        self.assertFalse(result['structure']['away'])

    @patch('nest_controller.requests.Session')
    def test_set_away_mode(self, mock_session_cls):
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updated": True}

        self.controller.session = mock_session
        mock_session.post.return_value = mock_response

        self.controller.set_away_mode("struct_1", True)

        # Verify call args
        args, kwargs = mock_session.post.call_args
        self.assertEqual(args[0], "https://transport.home.nest.com/v2/put/structure.struct_1")
        self.assertTrue(kwargs['json']['away'])
        self.assertIn('away_timestamp', kwargs['json'])

class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.mock_controller = MagicMock()
        # Use a temporary file for schedule
        self.test_file = 'test_schedule.json'
        self.scheduler = Scheduler(self.mock_controller, self.test_file)

    def tearDown(self):
        if hasattr(self, 'test_file') and os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_remove_event(self):
        event = self.scheduler.add_event("Monday", "12:00", "serial_1", 20.0)
        self.assertEqual(len(self.scheduler.get_schedule()), 1)
        self.assertEqual(event['temp'], 20.0)

        self.scheduler.remove_event(event['id'])
        self.assertEqual(len(self.scheduler.get_schedule()), 0)

import os
if __name__ == '__main__':
    unittest.main()
