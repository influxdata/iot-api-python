from flask import Flask, render_template
from api.helper_functions import get_current_time
from api import devices

app = Flask(__name__)


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


@app.route('/test')
def test():
    return "<p> Hello World </p>"


