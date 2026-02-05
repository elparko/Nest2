import unittest
from unittest.mock import MagicMock, patch
from nest_controller import NestController
import json

class TestNestController(unittest.TestCase):
    def setUp(self):
        self.config = {
            'issue_token': 'dummy_token',
            'cookies': 'dummy_cookies',
            'user_id': '12345'
        }
        self.controller = NestController(self.config)

    @patch('nest_controller.requests.Session')
    def test_get_status_success(self, mock_session_cls):
        # Setup mock response
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Sample simplified response structure based on what we expect
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
            "structure": {}
        }
        mock_response.json.return_value = mock_data

        # We need to inject the mock session into the controller because it's created in __init__
        # But here we are mocking the class, so subsequent instantiations would use it.
        # Since we already instantiated controller, we can just replace the session object.
        self.controller.session = mock_session
        mock_session.get.return_value = mock_response

        devices = self.controller.get_status()

        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]['serial'], 'serial_1')
        self.assertEqual(devices[0]['current_temperature'], 21.5)
        self.assertEqual(devices[0]['name'], 'Living Room')

        # Verify URL was correct
        mock_session.get.assert_called_with("https://transport.home.nest.com/v2/mobile/user.12345")

    @patch('nest_controller.requests.Session')
    def test_set_temperature(self, mock_session_cls):
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updated": True}

        self.controller.session = mock_session
        mock_session.post.return_value = mock_response

        result = self.controller.set_temperature("serial_1", 23.0)

        self.assertEqual(result, {"updated": True})

        # Verify call
        mock_session.post.assert_called_with(
            "https://transport.home.nest.com/v2/put/shared.serial_1",
            json={"target_change_pending": True, "target_temperature": 23.0}
        )

if __name__ == '__main__':
    unittest.main()
