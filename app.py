from flask import Flask, render_template
from api.helper_functions import get_current_time
from api import devices, write_data

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html', time=get_current_time())


@app.route('/help')
def help_page():
    return render_template('help.html', time=get_current_time())


@app.route('/devices')
def get_devices():
    device_id = 'todo'
    response = devices.get_device(device_id)
    # parse the response
    return render_template('devices.html', device=response.device_id)


@app.route('/create')
def create_device():
    response = devices.test_create_device()
    return render_template('create.html', response=response)


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
    # parse the response
    return render_template('buckets.html', buckets=buckets)


@app.route('/test')
def test():
    # buckets = devices.get_buckets()
    # return config.get('APP', 'INFLUX_URL')

    return render_template('help.html')
