from flask import Flask, render_template, request, jsonify, make_response
from api.helper_functions import get_current_time
from api import devices
import json
from influxdb_client.client.flux_table import FluxStructureEncoder

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html', time=get_current_time())


@app.route('/device/<string:device_id>', methods=['GET', 'POST'])
def get_device(device_id):
    result = devices.get_device(device_id)
    if not result:
        return render_template('devices.html', data=None)
    else:
        return render_template('devices.html', data=result)


@app.route('/devices/', methods=['GET', 'POST'])
def get_devices():
    result = devices.get_device(device_id=None)
    if not result:
        return render_template('devices.html', data=None)
    else:
        return render_template('devices.html', data=result)


@app.route('/create')
def create():
    return render_template('create.html', device_id=None)


# On submit function for /create
@app.route('/create_device', methods=['GET', 'POST'])
def create_device():
    if request.method == 'GET':
        return render_template('create.html', device_id=None)
    else:
        device_id = request.form.get('device_id_input', None)
        device_id = devices.create_device(device_id)
        return render_template('create.html', device_id=device_id)


@app.route('/buckets')
def get_buckets():
    buckets = devices.get_buckets()
    buckets = buckets.buckets
    return render_template('buckets.html', buckets=buckets)


@app.route('/auth')
def auth():
    response = devices.create_authorization('test_id')
    return render_template('auth.html')


@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'GET':
        return render_template('write.html', device_id=None)
    else:
        device_id = request.form.get('device_id_input', None)
        device_id = devices.write_measurements(device_id)
        return render_template('write.html', device_id=device_id)


@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'GET':
        return render_template('data.html', data=None)
    else:
        device_id = request.form.get('device_id_input', None)
        results = devices.get_measurements(device_id)
        return render_template('data.html', data=results)


# /api routes

@app.route('/api/buckets')
def api_get_buckets():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    buckets = devices.get_buckets()
    buckets = buckets.buckets
    return _corsify_actual_response(jsonify(buckets))

    
@app.route('/api/devices/<string:device_id>/measurements', methods=['POST'])
def api_get_measurements(device_id):
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    query = request.get_json()['query']
    if query is not None:
      data = devices.get_measurements(query)
      response = make_response(data, 200, {'content-type': 'application/csv'})
    else:
      response = make_response('Request is missing query', 404)  
    return _corsify_actual_response(response)


@app.route('/api/devices/<string:device_id>', methods=['GET', 'POST'])
def api_get_device(device_id):
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    return _corsify_actual_response(jsonify(devices.get_device(device_id)))


@app.route('/api/devices/generate', methods=['POST'])
def api_generate_data():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    data = devices.write_measurements(request.json['deviceIds'])
    return _corsify_actual_response(jsonify(data))


@app.route('/api/devices', methods=['GET'])
def api_get_devices():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    result = devices.get_device(device_id=None)
    data = json.dumps(result, cls=FluxStructureEncoder, indent=2)
    return _corsify_actual_response(make_response(data))


@app.route('/api/devices', methods=['POST'])
def api_create_device():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        device_id = devices.create_device(request.json['deviceId'])
        return _corsify_actual_response(jsonify({ 'deviceId': device_id}))
    else:
        return 'Content-Type not supported!'


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response