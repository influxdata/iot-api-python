from datetime import datetime

import configparser
import os
import urllib3
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

    # fix this
    device_id = uuid4()
    query_api = QueryApi(influxdb_client)


    device_filter = f"deviceId !== undefined ? flux` and r.deviceId == '${device_id}'` : flux` and r._field != 'token'"
    flux_query = f"from(bucket: {config.get('APP', 'INFLUX_BUCKET_AUTH')}) " \
                 f"|> range(start: 0) " \
                 f"|> filter(fn: (r) => r._measurement == 'deviceauth'{device_filter}) " \
                 f"|> last()"
    devices = {}

    query = ' from(bucket:"my-bucket")\
        |> range(start: -60m)\
        |> filter(fn:(r) => r._measurement == "deviceauth") '
    print(f"*** QUERY *** \n {flux_query}")
    # TODO FIX
    query_api.query(flux_query)
    return {}


def test_create_device():
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))

    device_id = str(uuid4())
    created_at = str(datetime.now())
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

    point = Point('deviceauth').tag("deviceId", device_id).\
        field('key', 'fake_auth_id').field('token', 'fake_auth_token')
    client_response = write_api.write(bucket=config.get('APP', 'INFLUX_BUCKET_AUTH'), record=point)

    return client_response

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
    buckets = buckets_api.find_bucket_by_name(config.get('APP', 'INFLUX_BUCKET_AUTH')) # function returns only 1 bucket
    bucket_id = buckets.buckets[0].id
    desc_prefix = 'IoTCenterDevice: '
    # get bucket_id from bucket
    org_resource = PermissionResource(org_id=config.get('APP', 'INFLUX_ORG'), type="orgs")
    read = Permission(action="read", resource=org_resource)
    write = Permission(action="write", resource=org_resource)
    permissions = [read, write]
    authorization = Authorization(org_id=config.get('APP', 'INFLUX_ORG'),
                                  permissions=permissions,
                                  description=desc_prefix + device_id)
    request = authorization_api.create_authorization(authorization)

    return request




