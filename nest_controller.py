import requests
import json
import time

class NestController:
    def __init__(self, config):
        """
        Initialize with config dictionary containing:
        - issue_token
        - cookies
        - user_id (optional, can be derived but better if provided)
        """
        self.issue_token = config.get('issue_token')
        self.cookies = config.get('cookies')
        self.user_id = config.get('user_id')
        self.session = requests.Session()

        # Headers mimicking a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Authorization': 'Basic ' + self.issue_token if self.issue_token else '',
            'Cookie': self.cookies
        })

    def get_status(self):
        """
        Fetches the current status of all devices and structure.
        Returns a dictionary with 'devices' list and 'structure' info.
        """
        if not self.user_id:
            raise ValueError("User ID is required to fetch status.")

        url = f"https://transport.home.nest.com/v2/mobile/user.{self.user_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            devices = []
            structure_info = {}

            shared_data = data.get('shared', {})
            structure_data = data.get('structure', {})

            # Extract Structure Info (assume single structure for simplicity, or take first)
            if structure_data:
                # structure_data is a dict of structure_ids -> info
                for s_id, s_info in structure_data.items():
                    structure_info = {
                        'structure_id': s_id,
                        'away': s_info.get('away'), # True/False (or boolean-like)
                        'name': s_info.get('name')
                    }
                    break # Just take the first one

            # Iterate through shared objects to find thermostats
            for serial, device_info in shared_data.items():
                if 'target_temperature' in device_info or 'current_temperature' in device_info:
                    device = {
                        'serial': serial,
                        'current_temperature': device_info.get('current_temperature'),
                        'target_temperature': device_info.get('target_temperature'),
                        'humidity': device_info.get('current_humidity'),
                        'hvac_mode': device_info.get('hvac_mode'),
                        'target_temperature_high': device_info.get('target_temperature_high'),
                        'target_temperature_low': device_info.get('target_temperature_low'),
                        'ambient_temperature': device_info.get('current_temperature'),
                        'name': device_info.get('name', serial)
                    }
                    devices.append(device)

            return {'devices': devices, 'structure': structure_info}

        except requests.exceptions.RequestException as e:
            print(f"Error fetching status: {e}")
            return {'devices': [], 'structure': {}}

    def set_temperature(self, serial, temperature):
        """
        Sets the target temperature for a specific device.
        """
        url = f"https://transport.home.nest.com/v2/put/shared.{serial}"
        payload = {
            "target_change_pending": True,
            "target_temperature": temperature
        }

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error setting temperature: {e}")
            return None

    def set_mode(self, serial, mode):
        """
        Sets the HVAC mode (heat, cool, heat-cool, off).
        """
        url = f"https://transport.home.nest.com/v2/put/shared.{serial}"
        payload = {
            "target_change_pending": True,
            "hvac_mode": mode
        }

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error setting mode: {e}")
            return None

    def set_away_mode(self, structure_id, away):
        """
        Sets the structure to Away (True) or Home (False).
        """
        url = f"https://transport.home.nest.com/v2/put/structure.{structure_id}"
        payload = {
            "away": away, # boolean
            "away_timestamp": int(time.time()),
            "away_setter": 0
        }

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error setting away mode: {e}")
            return None
