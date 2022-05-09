from flask import Flask, render_template, request
from api.helper_functions import get_current_time
from api import devices

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html', time=get_current_time())


@app.route('/devices', methods=['GET', 'POST'])
def get_devices():
    result = devices.get_device()
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
    # list of Bucket
    # bucket['name']
    # {'created_at': datetime.datetime(2022, 3, 15, 17, 22, 33, 731038, tzinfo=tzutc()),
    #  'description': None,
    #  'id': '11939869ae5f7415',
    #  'labels': [],
    #  'links': {'_self': '/api/v2/buckets/11939869ae5f7415',
    #            'labels': '/api/v2/buckets/11939869ae5f7415/labels',
    #            'members': '/api/v2/buckets/11939869ae5f7415/members',
    #            'org': '/api/v2/orgs/bea7ea952287f70d',
    #            'owners': '/api/v2/buckets/11939869ae5f7415/owners',
    #            'write': '/api/v2/write?org=bea7ea952287f70d&bucket=11939869ae5f7415'},
    #  'name': "sly's Bucket",
    #  'org_id': 'bea7ea952287f70d',
    #  'retention_rules': [{'every_seconds': 2592000,
    #                       'shard_group_duration_seconds': None,
    #                       'type': 'expire'}],
    #  'rp': None,
    #  'schema_type': 'implicit',
    #  'type': 'user',
    #  'updated_at': datetime.datetime(2022, 3, 15, 17, 22, 33, 731038, tzinfo=tzutc())}
    # parse the response and create a table instead
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