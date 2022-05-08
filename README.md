## Build a starter Python3 IoT app with the InfluxDB API and client libraries

## Introduction

This guide is for python developers who want to build Internet-of-Things (IoT) applications using the InfluxDB API and client libraries.
InfluxDB API client libraries are maintained by InfluxData and the user community. As a developer, client libraries enable you to take advantage of:
- idioms for InfluxDB requests, responses, and errors
- common patterns in a familiar programming language

In this guide, you'll walk through the basics of using the InfluxDB API and Python
client libraries in the context of building a real application as we
deconstruct the flow of events and data between the app, devices, and InfluxDB.
You'll see code samples that use InfluxDB API python client libraries to
manage IoT devices, write data to InfluxDB, query data from InfluxDB, create visualizations, and monitor the health of devices and the application itself.

From start to finish, you will:
- create a UI dashboard using Jinja
- install the influxdb-client package
- [create a configuration file for authentication with InfluxDB](#create-config.ini)
- [create a virtual IoT device](#create-iot-virtual-device)
- [store virtual IoT device to InfluxDB using the API](#store-virtual-iot-device-to-influxdb)
- [query bucket for IoT device using the API](#query-bucket-for-device)
- [write telemetry data to InfluxDB using the API](#write-telemetry-data)
- [query telemetry data in InfluxDB using the API](#query-telemetry-data)

## Contents
1. [Setup InfluxDB](#setup-influxdb)
1. [InfluxDB API basics](#influxdb-api-basics)
1. [Authorization and authentication in InfluxDB](#authorization-and-authentication-in-influxdb)
1. Start with an API client library
1. Create a bucket
  1. Measurements, time series
  2. Measurement schemas (aka bucket schemas)
1. [Write data to InfluxDB](#write-data-to-influxdb)
  1. Write line protocol
1. [Query InfluxDB](#query-influxdb)
  1. Send a Flux query
  1. Aggregate and downsample your data
1. Create data visualizations

## InfluxDB API basics

- [InfluxDB URL](#influxdb-url)
- [Data formats](#data-formats)
- [Responses](#responses)
- [Resources in InfluxDB](#resources-in-influxdb)

### InfluxDB URL

Throughout this guide, your application will send API requests to [your InfluxDB URL]().

```sh
http://localhost:8086
```

Most InfluxDB API operations you'll use in this guide are in the `/api/v2` URL path,
e.g.

```sh
http://localhost:8086/api/v2/query
http://localhost:8086/api/v2/write
```

### Data formats

#### Line protocol

You use the line protocol format to write data to InfluxDB.

#### CSV

The InfluxDB API returns query results in CSV format.

#### JSON

The InfluxDB API returns resources and errors in JSON format.

### Responses

The InfluxDB API is a REST API that accepts standard HTTP request verbs
and returns standard HTTP response codes. If InfluxDB sends a response body, the body
will have one of the following formats, depending on the endpoint and response status:

- JSON: responses with resources or error messages
- CSV: responses with query results.
- Plain text: some error responses, responses with system information

### Resources in InfluxDB

**Resources** are InfluxDB objects that store data (.e.g. buckets) or configuration (.e.g. tasks) in InfluxDB.
Your application uses the InfluxDB API to create, retrieve, update, and delete resources.
In this guide, you'll encounter the following commonly used InfluxDB resources:

- [Organization](#organization)
- [User](#user)
- [Authorization](#authorization)
- [Bucket](#bucket)

#### Organization

An **organization** in InfluxDB is a logical workspace for a group of users.
Members, buckets, tasks, and dashboards (along with a number of other resources), belong to an organization.

See how to find your organization.

#### User

Users in InfluxDB are granted permission to access the database.
Users are members of an **organization** and use **API tokens** to access resources.

#### Bucket

Buckets in InfluxDB are named locations where time series data is stored.
All buckets have a **retention policy***, a duration of time that each data point persists.
All buckets belong to an **organization**.

#### Authorization

An authorization in InfluxDB consists of a **token** and a set of **permissions**
that specify _read_ or _write_ access to InfluxDB **resources**.
Given that each authorization has one unique token, we use the term "API token" to refer to a token string and the authorization it belongs to.
InfluxDB uses API tokens to authenticate and authorize API requests.

#### Example: InfluxDB authorization

In the following example, API token `Qjnu6uskk8ibmaytsgAEH4swgVa72rA_dEqzJMstHYLYJcDPlfDCLmwcGZbyYP1DajQnnj==`
is a _Read-Write_ token with _read_ and _write_ access to all buckets
in organization `48c88459ee424a04`.

```json
{
   "id": "08e64ffe9b764000",
   "token": "Qjnu6uskk8ibmaytsgAEH4swgVa72rA_dEqzJMstHYLYJcDPlfDCLmwcGZbyYP1DajQnnj==",
   "status": "active",
   "description": "IoT Center: device3",
   "orgID": "48c88459ee424a04",
   "org": "iot-org",
   "userID": "0772396d1f411000",
   "user": "iot-app-owner",
   "permissions": [
     {
       "action": "read",
       "resource": {
         "type": "buckets",
         "orgID": "48c88459ee424a04",
         "org": "iot-org"
       }
     },
     {
       "action": "write",
       "resource": {
         "type": "buckets",
         "orgID": "48c88459ee424a04",
         "org": "iot-org"
       }
     }
   ]
 }
```

{{% caption %}}Response body from the GET `/api/v2/authorizations/AUTHORIZATION_ID` InfluxDB API endpoint{{% /caption %}}

{{% note %}}

To learn more about InfluxDB data elements, schemas, and design principles, see the
[Key concepts reference topics](influxdb/v2.1/reference/key-concepts/).

{{% /note %}}

## Create IoT Center Dashboard
You will be using Flask alongside Jinja to create your IoT Center application. 
Flask is a micro web framework that lets you develop web applications easily.
Jinja is a web template engine used to help render the UI. 


* Tutorial to install flask, jinja 
* Setting up the first index html

Before starting any new Python project, we should create a virtual environment for it.


```bash
$ mkdir iotproject
$ cd iotproject

# Create a new virtual environment named "virtualenv"
# Python 3.8+
$ python -m venv virtualenv

# Activate the virtualenv (OS X & Linux)
$ source virtualenv/bin/activate
```

Once your virtual environment has been activated, you will want to install Flask and Jinja. 
Python uses pip to manage dependencies, so you will use the following command.
```bash
$ pip install Flask
$ pip install Jinja
```

### Create a simple Flask Application
To spin up a simple Flask application, you will create a new file called ```app.py```.
```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
  return "Hello World!"
```

You can then run your new Flask application with the command ```flask run```. 
Open http://localhost:5000 in your browser, and you should now see the “Hello World!” response.

### Create the UI
You will now use Jinja to create html templates that will serve as your UI.  
You will first create an ```index.html``` page that will serve as your landing page. 

```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>IOT Center</title>
    </head>
    {% extends 'base.html' %}
    <body>
    {% block content %}
        <h1>Welcome to IOT Center</h1>
        <p>The current time is {{time}}</p>
    {% endblock %}
    
    </body>
</html>
```

Additionally, you will create a ```base.html``` that every html template will extend. You will also create your navbar
this file. Since every template will extend ```base.html``` we will also link bootstrap to this single page 

```html
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    <link rel="stylesheet" href="{{ url_for('static', filename= 'css/style.css') }}">
    <title>{% block title %} {% endblock %}</title>
  </head>
  <body>
    <nav class="navbar navbar-expand-md navbar-light bg-light">
        <a class="navbar-brand" href="{{ url_for('index')}}">IoT Center</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                <li class="nav-item">
                    <a class="nav-link" href="#">About</a>
                </li>
                <li>
                    <a class="nav-link" href="{{url_for('get_buckets')}}">Buckets</a>
                </li>
        </div>
    </nav>
    <div class="container">
        {% block content %} {% endblock %}
    </div>

    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
  </body>
</html>
```

Now that you have your Flask app running, we will now connect an InfluxDB instance to your app. 

## Install InfluxDB

If you don't already have an InfluxDB instance, [create an InfluxDB Cloud account](https://www.influxdata.com/products/influxdb-cloud/) or [install InfluxDB OSS](https://www.influxdata.com/products/influxdb/).

## Authenticate with an InfluxDB API token

### Add an InfluxDB All-Access token

For convenience in development, use an _All-Access_ token for your application to read and write with the InfluxDB API.
To create an All-Access token, use one of the following:
- [InfluxDB UI](influxdb/v2.1/security/tokens/create-token/#create-an-all-access-token)
- [InfluxDB CLI](/influxdb/v2.1/security/tokens/create-token/#create-an-all-access-token-1)

{{% note %}}

For a production application, we recommend you create a token with minimal permissions and only use it with that application.

{{% /note %}}

## Configure IoT App

### Create config.ini

The Python client library provides a client to easily interact with your InfluxDB instance. In order set up the client 
with the correct information with connect to your InfluxDB instance, we will need to create a configuration file that the
client can read from. 
The client needs the following information:

* your InfluxDB [API token](#authorization) with permission to query (_read_) buckets
and create (_write_) authorizations for IoT devices.
* your InfluxDB instance url
* your InfluxDB org ID
* your InfluxDB bucket names

We will create a file ```config.ini``` in the top level directory of your project and place the configuration info within it.
```ini
[APP]
INFLUX_URL = {{INFLUX_URL}}
INFLUX_TOKEN = {{INFLUX_TOKEN}}
INFLUX_ORG = {{INFLUX_ORG_ID}}
INFLUX_BUCKET = {{INFLUX_BUCKET_FOR_TELEMETRY}}
INFLUX_BUCKET_AUTH = {{INFLUX_BUCKET_FOR_DEVICES}}
```

The following is a sample configuration.
```ini
[APP]
INFLUX_URL = https://us-west-2-2.aws.cloud2.influxdata.com/
INFLUX_TOKEN = 52Pc_ZkJsRh1PKzlwrK8yO6jWSDh6WPAHbfqp-5aROz4zBnY2mvkKws9YoYzksGH3_Xp90rVqo2PRiajTxaUcw==
INFLUX_ORG = bea7ea952287f70d
INFLUX_BUCKET = sly's Bucket
INFLUX_BUCKET_AUTH = devices_auth
```


## Create IoT Virtual Device
You will now create a virtual IoT device. This device will generate weather data that you will store in InfluxDB. 
Create a new directory called ```api``` under the top level and create a new file called ```sensor.py``` within the new directory.

[//]: # Probably preferable to link the file rather than have the whole file written up()
```python
import json
import random
import urllib3


http = urllib3.PoolManager()


# Helper function to fetch lat lon data
def fetch_json(url):
    """Fetch JSON from url."""
    response = http.request('GET', url)
    if not 200 <= response.status <= 299:
        raise Exception(f'[HTTP - {response.status}]: {response.reason}')
    config_fresh = json.loads(response.data.decode('utf-8'))
    return config_fresh


class Sensor:
    def __init__(self):
        self.id = ''
        self.temperature = None
        self.pressure = None
        self.humidity = None
        self.geo = None

    def generate_measurement(self):
        return round(random.uniform(0, 100))

    def geo(self):
        """
        Get GEO location from https://freegeoip.app/json/'.
        :return: Returns a dictionary with `latitude` and `longitude` key.
        """
        try:
            return fetch_json('https://freegeoip.app/json/')
        except Exception:
            return {
                'latitude':  self.generate_measurement(),
                'longitude':  self.generate_measurement(),
            }
```

You will be using this Sensor object and its function ```generate_measurement()``` to simulate weather data.


## Store Virtual IoT Device to InfluxDB
You will now learn how to use the python client library to store the virtual device information within InfluxDB.
Within your InfluxDB instance, you will have at least two buckets set up. 
We will use the first bucket to store device information for your virtual device.
The other bucket will be used to store telemetry data which we will learn more about later on in this guide.  

Create a new file called ```devices.py``` within your ```api``` directory. This file will hold the core functionality for your app.

```python
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
```

The file imports all the necessary functionality that we will need for this app from ```influxdb_client```.
At the top of the file, we read in our configuration file created earlier through 
```python
config = configparser.ConfigParser()
config.read('config.ini')
```

```create_device``` stores your virtual device data by reading in a device_id and writing that information over to your first bucket.
We begin by first initializing ```influxdb_client``` using our config. ```InfluxDBClient``` needs your url, token and org in order to
create a connection to your InfluxDB instance.
```python
influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                  token=config.get('APP', 'INFLUX_TOKEN'),
                                  org=config.get('APP', 'INFLUX_ORG'))
```

Using the ```InfluxDBClient``` we create a ```WriteApi``` instance that will allow us to write a record to a specified bucket.
We then create the record we want to write to the bucket using ```Point```. In this case, ```deviceauth``` is the name 
of the ```_measurement```. We use ```deviceId``` as the tag, and we include two separate fields named ```key``` and ```token``` to store 
the device authorization information (more information on authorization will be provided further along in the guide). 
We then use ```write_api``` to send the API request and write the record to your bucket. 
```write_api``` returns ```None``` on success, so we check for any failures then return the ```device_id``` if the request
was successful.
```python
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

## Query Bucket For Device
Now that we have written data to a bucket, you will now learn how use the client library to query for the device information.  

Within ```devices.py``` create a new function called ```get_devices()```. This function will take in a ```device_id``` and 
return a list of tuples that represent the records generated by the query.
```python
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

   results = []
       for table in response:
           for record in table.records:
               results.append((record.get_field(), record.get_value()))
    return results
```

Using the ```InfluxDBClient``` we create a ```QueryApi``` instance that will allow us to query a records from a specified bucket.
Here we generate the query itself using Flux. Within the query, we set the bucket information, range, and query filter.
Our query filters on ```_measurement``` ```deviceauth``` and searches for any device_id that that matches our passed in device_id.
Additionally, we add a clause to search for ```_field```s that do not contain ```token``` as a value.
```python
device_filter = f'r.deviceId == "{device_id}" and r._field != "token"'
flux_query = f'from(bucket: "{config.get("APP", "INFLUX_BUCKET_AUTH")}") ' \
           f'|> range(start: 0) ' \
           f'|> filter(fn: (r) => r._measurement == "deviceauth" and {device_filter}) ' \
           f'|> last()'
```

We send this query using the client and the client returns a ```FluxTable``` that we then parse into a list of tuples.
```python
# Samples results
[('key', 'fake_auth_id_1'), ('key', 'fake_auth_id_2')]
```

## Write Telemetry Data
Now that you know how to write data to a bucket, we will simulate telemetry data and write over to InfluxDB.  

Within ```devices.py``` create a new function called ```write_measurements()```. This function will take in a ```device_id```
and write simulated weather telemetry data to your second bucket.  
We begin again by initializing our ```WriteAPI``` instance. We then initialize our ```Sensor``` and create a ```Point```
that contains data for temperature, humidity, pressure, lat, and lon. We set the ```_measurement``` to ```environment```
and use that as the main reference for our future queries.

```python
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
```

## Query Telemetry Data
Once the telemetry data has been written into your bucket, you can send queries to InfluxDB to retrieve that data.  

Within ```devices.py``` create a new function called ```get_measurements()```. This function will take in a ```device_id```
and query for simulated weather telemetry data produced by your virtual device. Here we query the ```_measurement```
```environment``` and query for all records where ```device``` matches the ```device_id```. We then parse the ```FluxTable```
and return each record as a dict containing all the information from each record returned.

```python
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
```

We then parse the ```FluxTable``` and return each record as a dict containing all the information from each record returned.

```python
# iterate through the result(s)
    results = []
    for table in response:
        results.append(table.records[0].values)

    return results
```
```python
[
   {
      'result': '_result', 
       'table': 0, 
       '_start': datetime.datetime(1970, 1, 1, 0, 0, tzinfo=tzutc()), 
       '_stop': datetime.datetime(2022, 5, 8, 22, 25, 10, 111697, tzinfo=tzutc()), 
       '_time': datetime.datetime(2022, 5, 5, 17, 25, 48, 57014, tzinfo=tzutc()), 
       '_value': 33.780799865722656, 
       'HumiditySensor': 'virtual_bme280', 
       'PressureSensor': 'virtual_bme280', 
       'TemperatureSensor': 'virtual_bme280', 
       '_field': 'Lat', 
       '_measurement': 'environment', 
       'device': 'test_device_508472435243'
    }
]
```


## Create Virtual Device Authorization with API 
You will now learn how to use the python client library to create authorization for the virtual device.
Authorization will give read/write permissions to your virtual device which will allow it to send data to InfluxDB.
Within your InfluxDB instance, you will have at least two buckets set up. 
We will use one of the buckets to store authorization information for your virtual device.
The other bucket will be used to store telemetry data which we will learn more about later on in this guide. 

Create a new file called ```devices.py``` within your ```api``` directory. 

```python
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
```

```create_authorization()```


## Send API Requests
Now that you have InfluxDB, an API token, and the Python client library, you will use the client library to send a request to the InfluxDB API.


#### Example: list API endpoints

Use a client library to retrieve a list of InfluxDB API endpoints.

{{% api-endpoint method="GET" endpoint="http://localhost:8086/api/v2"%}}

{{< code-tabs-wrapper >}}
{{% code-tabs %}}
[Node.js](#nodejs)
{{% /code-tabs %}}
{{% code-tab-content %}}

1. Copy the example below and replace the INFLUX_URL and INFLUX_TOKEN values with your own.

```js

#!/usr/bin/env node

const { InfluxDB } = require('@influxdata/influxdb-client')
const { RootAPI } = require('@influxdata/influxdb-client-apis')

const INFLUX_URL='http://192.168.1.2:8086'
const INFLUX_TOKEN='29Ye1KH9VkASPR2DSfRfFd82OwGD-5HWkBj0Ju_m-DTgT4PHakgweD3p87mp45Y633njDllKkD5wVc0zMCVhIw=='

const influxdb = new InfluxDB({url: INFLUX_URL, token: INFLUX_TOKEN})
const rootAPI = new RootAPI(influxdb)

rootAPI.getRoutes().then(routes => console.log(routes))

```

2. From your `iot-center-v2` directory, launch the `node` REPL.

```sh

node

```

3. At the prompt, paste the example code (from _Step 1_) and press `Enter`.

{{% /code-tab-content %}}
{{< /code-tabs-wrapper >}}




## Introducing IoT Center

The IoT Center architecture has four layers:

- **InfluxDB API**: InfluxDB v2 API.
- **IoT device**: Virtual or physical devices write IoT data to the InfluxDB API.
- **IoT Center UI**: User interface sends requests to IoT Center server and renders views for the browser.
- **IoT Center server**: Server and API receives requests from the UI, sends requests to InfluxDB,
  and processes responses from InfluxDB.

### IoT Center: register and list IoT devices

The IoT Center **Device Registrations** page lists registered IoT devices
and lets you register new devices.
In IoT Center, a **registered device** is a virtual or physical IoT device with a unique InfluxDB authorization.
For each registered device, you can do the following:
- view a dashboard with data visualizations
- view configuration
- remove the device

### IoT Center: register a device

When you click the "Register" button, IoT Center UI sends a request to the `/api/devices/DEVICE_ID` IoT Center server endpoint. In response, IoT Center server queries InfluxDB to find a point with device ID in `INFLUX_BUCKET_AUTH`.
If no point exists (i.e., the device is not registered), IoT Center server uses the InfluxDB client library to send the following API requests:

2. `POST` request to `/api/v2/write` writes a `deviceauth` point with device ID to `INFLUX_BUCKET_AUTH` bucket.
3. `POST` request to `/api/v2/authorizations` creates an authorization with the description **IoT Center: `DEVICE_ID`** and write permission to the `INFLUX_BUCKET` bucket.
4. `POST` request  to `/api/v2/write` writes a `deviceauth` point with device ID, API token, and authorization ID to `INFLUX_BUCKET_AUTH`.


### IoT Center: list registered devices

To list registered devices, the IoT Center UI [DevicesPage](https://github.com/bonitoo-io/iot-center-v2/blob/3118c6576ad7bccf0b84b63f95350bdaa159324e/app/ui/src/pages/DevicesPage.tsx) component sends a request to the `/api/devices` IoT Center server endpoint.
{{/* Source: https://github.com/bonitoo-io/iot-center-v2/blob/3118c6576ad7bccf0b84b63f95350bdaa159324e/app/ui/src/pages/DevicesPage.tsx */}}

When IoT Center server receives the request, the server calls the [`getDevices()`](ttps://github.com/bonitoo-io/iot-center-v2/blob/f5b4a0b663e2e14bcd4f6fddb35cab2de216e6b6/app/server/influxdb/devices.js#L16) function.
`getDevices()` does the following:

1. Instantiates a query client from the InfluxDB client library.
2. Builds a Flux query to retrieve all points with the `deviceauth` measurement from
   the `INFLUX_BUCKET_AUTH` bucket.
3. Returns a `Promise` that sends the query to the `/api/v2/query` InfluxDB API endpoint and iterates over devices in the response.

#### Example

{{< code-tabs-wrapper >}}
{{% code-tabs %}}
[Node.js](#nodejs)
{{% /code-tabs %}}
{{% code-tab-content %}}

Flux query for devices in InfluxDB.
The query doesn't return device API tokens unless a device ID is specified.

```js

const deviceFilter =
  deviceId !== undefined
    ? flux` and r.deviceId == "${deviceId}"`
    : flux` and r._field != "token"`
const fluxQuery = flux`from(bucket:${INFLUX_BUCKET_AUTH})
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "deviceauth"${deviceFilter})
  |> last()`

```

{{% /code-tab-content %}}
{{< /code-tabs-wrapper >}}

{{% caption %}}[/app/server/influxdb/devices.js line 18](https://github.com/bonitoo-io/iot-center-v2/blob/f5b4a0b663e2e14bcd4f6fddb35cab2de216e6b6/app/server/influxdb/devices.js#L18){{% /caption %}}

### IoT Center: device details

IoT Center displays configuration details for a registered IoT device.
IoT Center API composes device configuration from the device's authorization and your InfluxDB configuration properties.

