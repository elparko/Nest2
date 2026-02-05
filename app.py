from flask import Flask, render_template, jsonify, request
import json
import os
from nest_controller import NestController

app = Flask(__name__)

# Load configuration
CONFIG_FILE = 'config.json'
if not os.path.exists(CONFIG_FILE):
    print(f"Warning: {CONFIG_FILE} not found. Please copy config.json.example to config.json and update credentials.")
    # Create a dummy config so the app doesn't crash immediately, but it won't work.
    config = {}
else:
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

controller = NestController(config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    if not config:
        return jsonify({'error': 'Config not found'}), 500

    devices = controller.get_status()
    return jsonify({'devices': devices})

@app.route('/api/control', methods=['POST'])
def control_device():
    if not config:
        return jsonify({'error': 'Config not found'}), 500

    data = request.json
    serial = data.get('serial')
    action = data.get('action') # 'set_temp' or 'set_mode'
    value = data.get('value')

    if not serial or not action:
        return jsonify({'error': 'Missing serial or action'}), 400

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

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible on local network
    app.run(host='0.0.0.0', port=5000, debug=False)
