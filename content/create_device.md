#### Example: create a device

{{< code-tabs-wrapper >}}
{{% code-tabs %}}
[python3](#python)
{{% /code-tabs %}}
{{% code-tab-content %}}

The IoT Center server IoT Center `create_device()` function uses [`@influxdata/influxdb-client-apis`]() to create an authorization
and write device information to a bucket within InfluxDB.

```python
def create_device(device_id=None):
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=os.environ.get('INFLUX_TOKEN'),
                                     org=os.environ.get('INFLUX_ORG'))

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
```
