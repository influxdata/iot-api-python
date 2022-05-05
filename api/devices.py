from datetime import datetime

import configparser
import json
import random
import os
import urllib3
from datetime import datetime
from typing import Optional
from uuid import uuid4
from influxdb_client import Authorization, InfluxDBClient, Permission, PermissionResource, Point, WriteOptions
from influxdb_client.client.query_api import QueryOptions
from influxdb_client.client.authorizations_api import AuthorizationsApi
from influxdb_client.client.bucket_api import BucketsApi
from influxdb_client.client.query_api import QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS

# Set up configuration file needed to reach influxdb
# config = {
#     "id": os.getenv("VIRTUAL_DEVICE_NAME"),
#     "influx_url": os.getenv("INFLUX_URL"),
#     "influx_token": os.getenv("INFLUX_TOKEN"),
#     "influx_org": os.getenv("INFLUX_ORG"),
#     "influx_bucket": os.getenv("INFLUX_BUCKET"),
#     "influx_bucket_auth": os.getenv("INFLUX_BUCKET_AUTH")
# }

config = configparser.ConfigParser()
config.read('config.ini')
http = urllib3.PoolManager()


def generate_measurement():
    return round(random.uniform(0, 100))


def measure():
    """
    Get measure from bme280 or default values.
    :return: Returns object with properties: temperature, pressure and humidity.
    """

    measurements = {
        "temperature": generate_measurement(),
        "pressure": generate_measurement(),
        "humidity": generate_measurement()
    }
    return measurements


def geo():
    """
    Get GEO location from https://freegeoip.app/json/'.
    :return: Returns a dictionary with `latitude` and `longitude` key.
    """
    try:
        return fetch_json('https://freegeoip.app/json/')
    except Exception:
        return {
            'latitude':  generate_measurement(),
            'longitude':  generate_measurement(),
        }


def fetch_json(url):
    """Fetch JSON from url."""
    response = http.request('GET', url)
    if not 200 <= response.status <= 299:
        raise Exception(f'[HTTP - {response.status}]: {response.reason}')
    config_fresh = json.loads(response.data.decode('utf-8'))
    return config_fresh


def get_config():
    print(config.get('APP', 'INFLUX_URL'))
    return config


def get_buckets():
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))

    buckets_api = influxdb_client.buckets_api()
    buckets = buckets_api.find_buckets()
    return buckets


# this checks if the device is already in the auth bucket
# Should probably return a device

#  Gets devices or a particular device when deviceId is specified. Tokens
#  are not returned unless deviceId is specified. It can also return devices
#  with empty/unknown key, such devices can be ignored (InfluxDB authorization is not associated).
#  @param deviceId optional deviceId
#  @returns promise with an Record<deviceId, {deviceId, createdAt, updatedAt, key, token}>.

def get_device(device_id) -> {}:
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))

    # Queries must be formatted with single and double quotes correctly
    query_api = QueryApi(influxdb_client)
    device_id = str(device_id)
    device_filter = f'r.deviceId == "{device_id}" and r._field != "token"'
    flux_query = f'from(bucket: "{config.get("APP", "INFLUX_BUCKET_AUTH")}") ' \
                 f'|> range(start: 0) ' \
                 f'|> filter(fn: (r) => r._measurement == "deviceauth" and {device_filter}) ' \
                 f'|> last()'
    devices = {}

    response = query_api.query(flux_query)

    # iterate through the result(s)
    # TODO maybe change this to only show, device_id, auth_id, auth_token?
    results = []
    for table in response:
        for record in table.records:
            results.append((record.get_field(), record.get_value()))
    return results


def test_create_device(device_id=None):
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))

    if device_id is None:
        device_id = str(uuid4())

    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

    point = Point('deviceauth') \
        .tag("deviceId", device_id) \
        .field('key', f'fake_auth_id_{device_id}') \
        .field('token', f'fake_auth_token_{device_id}')

    client_response = write_api.write(bucket=config.get('APP', 'INFLUX_BUCKET_AUTH'), record=point)

    # write() returns None on success
    if client_response is None:
        return device_id

    # Return None on failure
    return None


def write_measurements(device_id):
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

    coord = geo()

    point = Point("environment") \
        .tag("device", device_id) \
        .tag("TemperatureSensor", "virtual_bme280") \
        .tag("HumiditySensor", "virtual_bme280") \
        .tag("PressureSensor", "virtual_bme280") \
        .field("Temperature", generate_measurement()) \
        .field("Humidity", generate_measurement()) \
        .field("Pressure", generate_measurement()) \
        .field("Lat", coord['latitude']) \
        .field("Lon", coord['longitude']) \
        .time(datetime.utcnow())

    print(f"Writing: {point.to_line_protocol()}")
    client_response = write_api.write(bucket=config.get('APP', 'INFLUX_BUCKET'), record=point)

    # write() returns None on success
    if client_response is None:
        # TODO Maybe also return the data that was written
        return device_id

    # Return None on failure
    return None


# Creates an authorization for a deviceId and writes it to a bucket
def create_device(device_id) -> Authorization:
    device = get_device(device_id)
    # TODO actually need to set up and run this
    authorization_valid = device["key"]
    if authorization_valid:
        print(f"{device} \n This device ID is already registered and has an authorization.")
    else:
        print(f"createDeviceAuthorization: deviceId ={device_id}")
        authorization = create_authorization(device_id)
        influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                         token=config.get('APP', 'INFLUX_TOKEN'),
                                         org=config.get('APP', 'INFLUX_ORG'))

        write_api = influxdb_client.write_api(write_options=WriteOptions(batch_size=1))
        point = Point("deviceauth") \
            .tag("deviceId", device_id) \
            .field("key", authorization.id) \
            .field("token", authorization.token)
        write_api.write(bucket=config.get('APP', 'INFLUX_BUCKET_AUTH'), record=point)
        write_api.close()
        return authorization


# TODO
# Function should return a response code
# Creates an authorization for a supplied deviceId
def create_authorization(device_id) -> Authorization:
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))

    authorization_api = AuthorizationsApi(influxdb_client)

    buckets_api = BucketsApi(influxdb_client)
    buckets = buckets_api.find_bucket_by_name(config.get('APP', 'INFLUX_BUCKET_AUTH'))  # function returns only 1 bucket
    bucket_id = buckets.id
    org_id = buckets.org_id
    desc_prefix = f'IoTCenterDevice: {device_id}'
    # get bucket_id from bucket
    org_resource = PermissionResource(org_id=config.get('APP', 'INFLUX_ORG'), type="buckets")
    read = Permission(action="read", resource=org_resource)
    write = Permission(action="write", resource=org_resource)
    permissions = [read, write]
    # authorization = Authorization(org_id=config.get('APP', 'INFLUX_ORG'),
    #                               permissions=permissions,
    #                               description=desc_prefix)

    authorization = Authorization(org_id=config.get('APP', 'INFLUX_ORG'),
                                  permissions=permissions,
                                  description=desc_prefix)

    # request = authorization_api.find_authorizations()
    # return request

    # request = authorization_api.create_authorization(authorization)
    # return request

    request = authorization_api.create_authorization(org_id=org_id, permissions=permissions)
    return request




