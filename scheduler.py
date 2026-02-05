import json
import time
import threading
import os
from datetime import datetime

class Scheduler:
    def __init__(self, nest_controller, schedule_file='schedule.json'):
        self.controller = nest_controller
        self.schedule_file = schedule_file
        self.running = False
        self.schedule = self.load_schedule()

    def load_schedule(self):
        if not os.path.exists(self.schedule_file):
            return []
        try:
            with open(self.schedule_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def save_schedule(self):
        with open(self.schedule_file, 'w') as f:
            json.dump(self.schedule, f, indent=2)

    def add_event(self, day, time_str, serial, temp):
        """
        day: "Monday", "Tuesday", etc.
        time_str: "HH:MM" (24h)
        serial: thermostat serial
        temp: target temperature
        """
        event = {
            "id": int(time.time() * 1000), # Simple unique ID
            "day": day,
            "time": time_str,
            "serial": serial,
            "temp": float(temp)
        }
        self.schedule.append(event)
        self.save_schedule()
        return event

    def remove_event(self, event_id):
        self.schedule = [e for e in self.schedule if e.get('id') != event_id]
        self.save_schedule()

    def get_schedule(self):
        return self.schedule

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        print("Scheduler started.")
        while self.running:
            now = datetime.now()
            current_day = now.strftime("%A")
            current_time = now.strftime("%H:%M")

            # Check every minute
            # To avoid multiple triggers in the same minute, we sleep for 60s
            # But simpler: check if event matches, and if we haven't triggered it yet?
            # For simplicity in this robust version:
            # We will sleep until the start of the next minute to avoid double triggers or missing.

            for event in self.schedule:
                if event['day'] == current_day and event['time'] == current_time:
                    print(f"Triggering schedule event: {event}")
                    self.controller.set_temperature(event['serial'], event['temp'])

            # Sleep for 60 seconds (naive implementation)
            # Better: sleep(60 - seconds)
            sleep_time = 60 - now.second
            time.sleep(sleep_time)
