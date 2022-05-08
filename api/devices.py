import configparser
from datetime import datetime
from uuid import uuid4
from influxdb_client import Authorization, InfluxDBClient, Permission, PermissionResource, Point, WriteOptions
from influxdb_client.client.authorizations_api import AuthorizationsApi
from influxdb_client.client.bucket_api import BucketsApi
from influxdb_client.client.query_api import QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS

from api.sensor import Sensor

config = configparser.ConfigParser()
config.read('config.ini')

# TODO use global instance after tutorial guide has been written
# influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
#                                  token=config.get('APP', 'INFLUX_TOKEN'),
#                                  org=config.get('APP', 'INFLUX_ORG'))


def get_buckets():
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))

    buckets_api = influxdb_client.buckets_api()
    buckets = buckets_api.find_buckets()
    return buckets


def get_device() -> {}:
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))

    # Queries must be formatted with single and double quotes correctly
    query_api = QueryApi(influxdb_client)
    # query_api = influxdb_client.query_api()
    # device_id = str(device_id)
    device_filter = f'r._field != "token"'
    flux_query = f'from(bucket: "{config.get("APP", "INFLUX_BUCKET_AUTH")}") ' \
                 f'|> range(start: 0) ' \
                 f'|> filter(fn: (r) => r._measurement == "deviceauth" and {device_filter}) ' \
                 f'|> last()'
    devices = {}

    response = query_api.query(flux_query)

    # iterate through the result(s)
    # TODO maybe change this to only show, device_id, auth_id, auth_token?
    # iterate through the result(s)
    results = []
    for table in response:
        results.append(table.records[0].values)

    return results


def create_device(device_id=None):
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
    virtual_device = Sensor()
    coord = virtual_device.geo()

    point = Point("environment") \
        .tag("device", device_id) \
        .tag("TemperatureSensor", "virtual_bme280") \
        .tag("HumiditySensor", "virtual_bme280") \
        .tag("PressureSensor", "virtual_bme280") \
        .field("Temperature", virtual_device.generate_measurement()) \
        .field("Humidity", virtual_device.generate_measurement()) \
        .field("Pressure", virtual_device.generate_measurement()) \
        .field("Lat", coord['latitude']) \
        .field("Lon", coord['latitude']) \
        .time(datetime.utcnow())

    print(f"Writing: {point.to_line_protocol()}")
    client_response = write_api.write(bucket=config.get('APP', 'INFLUX_BUCKET'), record=point)

    # write() returns None on success
    if client_response is None:
        # TODO Maybe also return the data that was written
        return device_id

    # Return None on failure
    return None


def get_measurements(device_id):
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))

    # Queries must be formatted with single and double quotes correctly
    query_api = QueryApi(influxdb_client)
    device_id = str(device_id)
    device_filter = f'r.device == "{device_id}"'
    flux_query = f'from(bucket: "{config.get("APP", "INFLUX_BUCKET")}") ' \
                 f'|> range(start: 0) ' \
                 f'|> filter(fn: (r) => r._measurement == "environment" and {device_filter}) ' \
                 f'|> last()'

    response = query_api.query(flux_query)

    # iterate through the result(s)
    results = []
    for table in response:
        results.append(table.records[0].values)

    return results


# Creates an authorization for a deviceId and writes it to a bucket
# def create_device(device_id) -> Authorization:
#     device = get_device(device_id)
#     # TODO actually need to set up and run this
#     authorization_valid = device["key"]
#     if authorization_valid:
#         print(f"{device} \n This device ID is already registered and has an authorization.")
#     else:
#         print(f"createDeviceAuthorization: deviceId ={device_id}")
#         authorization = create_authorization(device_id)
#         influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
#                                          token=config.get('APP', 'INFLUX_TOKEN'),
#                                          org=config.get('APP', 'INFLUX_ORG'))
#
#         write_api = influxdb_client.write_api(write_options=WriteOptions(batch_size=1))
#         point = Point("deviceauth") \
#             .tag("deviceId", device_id) \
#             .field("key", authorization.id) \
#             .field("token", authorization.token)
#         write_api.write(bucket=config.get('APP', 'INFLUX_BUCKET_AUTH'), record=point)
#         write_api.close()
#         return authorization


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




