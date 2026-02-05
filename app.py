from flask import Flask, render_template, jsonify, request
import json
import os
from nest_controller import NestController
from scheduler import Scheduler

app = Flask(__name__)

# Load configuration
CONFIG_FILE = 'config.json'
if not os.path.exists(CONFIG_FILE):
    print(f"Warning: {CONFIG_FILE} not found. Please copy config.json.example to config.json and update credentials.")
    config = {}
else:
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

controller = NestController(config)
scheduler = Scheduler(controller)
scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    if not config:
        return jsonify({'error': 'Config not found'}), 500

    # get_status now returns {'devices': [], 'structure': {}}
    data = controller.get_status()
    return jsonify(data)

@app.route('/api/control', methods=['POST'])
def control_device():
    if not config:
        return jsonify({'error': 'Config not found'}), 500

    data = request.json
    action = data.get('action')

    # Structure control doesn't need serial
    if action == 'set_away':
        structure_id = data.get('structure_id')
        away = data.get('away') # boolean
        if not structure_id:
            return jsonify({'error': 'Missing structure_id'}), 400
        result = controller.set_away_mode(structure_id, away)
        if result:
            return jsonify({'success': True, 'result': result})
        return jsonify({'error': 'Failed to set away mode'}), 500

    # Device control
    serial = data.get('serial')
    value = data.get('value')

    if not serial:
        return jsonify({'error': 'Missing serial'}), 400

    result = None
    if action == 'set_temp':
        result = controller.set_temperature(serial, value)
    elif action == 'set_mode':
        result = controller.set_mode(serial, value)
    else:
        return jsonify({'error': 'Invalid action'}), 400

    if result:
        return jsonify({'success': True, 'result': result})
    else:
        return jsonify({'error': 'Failed to update device'}), 500

@app.route('/api/schedule', methods=['GET', 'POST', 'DELETE'])
def handle_schedule():
    if request.method == 'GET':
        return jsonify(scheduler.get_schedule())

    if request.method == 'POST':
        data = request.json
        # Check required fields
        if not all(k in data for k in ('day', 'time', 'serial', 'temp')):
             return jsonify({'error': 'Missing fields'}), 400
        event = scheduler.add_event(data['day'], data['time'], data['serial'], data['temp'])
        return jsonify(event)

    if request.method == 'DELETE':
        event_id = request.json.get('id')
        scheduler.remove_event(event_id)
        return jsonify({'success': True})

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible on local network
    app.run(host='0.0.0.0', port=5000, debug=False)
