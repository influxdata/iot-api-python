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
- create a configuration file for authentication with InfluxDB
- create a virtual IoT device
- write telemetry data to InfluxDB
- query telemetry data in InfluxDB

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

## Send an API request

Now that you have InfluxDB, an API token, and the Node.JS client library (with `iot-center-v2`), use the client library to send a request to the InfluxDB API.

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


## Configure IoT Center

env.js

### Add your InfluxDB API token

IoT Center server needs an [API token](#authorization) with permission to query (_read_) buckets
and create (_write_) authorizations for IoT devices.
Use the All-Access token you created in [Add an InfluxDB All-Access token](#add-an-influxdb-all-access-token).

### Add your InfluxDB URL

### Add your InfluxDB organization

### Introducing IoT Center

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

#### Example: create a device

{{< code-tabs-wrapper >}}
{{% code-tabs %}}
[Node.js](#nodejs)
{{% /code-tabs %}}
{{% code-tab-content %}}

The IoT Center server IoT Center `createDevice()` function uses [`@influxdata/influxdb-client-apis`]() to create an authorization
and write device information to InfluxDB.

```js
async function createDevice(deviceId) {
  console.log(`createDevice: deviceId=${deviceId}`)

  const writeApi = influxdb.getWriteApi(INFLUX_ORG, INFLUX_BUCKET_AUTH)
  const createdAt = new Date().toISOString()
  const point = new Point('deviceauth')
    .tag('deviceId', deviceId)
    .stringField('createdAt', createdAt)
  writeApi.writePoint(point)
  await writeApi.close()
  const {id: key, token} = await createDeviceAuthorization(deviceId)
  return {deviceId, createdAt, key, token}
}
```

{{% /code-tab-content %}}
{{< /code-tabs-wrapper >}}

{{% caption %}} IoT Center [/app/server/influxdb/authorizations.js](https://github.com/bonitoo-io/iot-center-v2/blob/b3bfce7ee9f5f045cfc8d881a9819f5dd9ad7a35/app/server/influxdb/authorizations.js#L61){{% /caption %}}

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

#### Example

https://github.com/bonitoo-io/iot-center-v2/blob/10fd78e67ccf093dedbed9eed88439423203c8a2/app/server/apis/index.js#L58

### IoT Center: unregister a device

To _unregister_ a device, IoT Center deletes the device authorization from your InfluxDB organization with the following steps:

1. When you click the "Delete" button, IoT Center UI sends a `DELETE` request to the `/api/devices/DEVICE_ID` IoT Center API endpoint.
2. IoT Center server retrieves the list of IoT Center authorizations and finds the authorization that matches the device ID.
3. IoT Center sends a `DELETE` request to the `/api/v2/authorizations/AUTHORIZATION_ID` InfluxDB API endpoint.

## Write data to InfluxDB

{{% note %}}

To learn more, see [Write data with the API](/influxdb/v2.1/write-data/developer-tools/api/)

{{% /note %}}

### Batch writes with client libraries

#### Batch writes with the Javascript client library

[influxdb-client-js](https://github.com/influxdata/influxdb-client-js/) provides features like batch writes, retries, and error handling necessary for production-ready applications.
Batch writes reduce network use to make your application more efficient.
1. to instantiate a point writer from the
2. The [`writeApi.writePoint(point)`](https://github.com/influxdata/influxdb-client-js/blob/d76b1fe8c4000d7614f44d696c964cc4492826c6/packages/core/src/impl/WriteApiImpl.ts#L256) function converts each new point to [line protocol]() and adds the line to an array in a `WriteBuffer` object.
3. [`writeApi.flush()`]() invokes the WriteBuffer's [`writeApi.sendBatch()`](https://github.com/influxdata/influxdb-client-js/blob/d76b1fe8c4000d7614f44d696c964cc4492826c6/packages/core/src/impl/WriteApiImpl.ts#L147)
function to batch the points and send each batch to the
InfluxDB `/api/v2/write` endpoint.

{{% api-endpoint method="POST" endpoint="/api/v2/write" %}}

### IoT Center: write device data to InfluxDB

The IoT Center **virtual device** emulates a real IoT device by generating measurement data and writing the data to InfluxDB.
Use the virtual device to demonstrate the IoT Center dashboard and test the InfluxDB API before you advance to adding physical devices or other clients.

IoT Center provides a "Write Missing Data" button that generates `environment`
(temperature, humidity, pressure, CO2, TVOC, latitude, and longitude) [measurement]() data for the virtual device.
The button generates measurements for every minute over the last seven days and
writes the generated measurement data to the InfluxDB bucket you configured.

To write the measurements to the bucket, IoT Center uses the `writeEmulatedData(...)` function
in **DevicePage.tsx**. `writeEmulatedData(...)` takes the following steps to write data to InfluxDB:
1. Configures a new instance of the InfluxDB client
   ```js
   const influxDB = new InfluxDB({url, token})
   ```
2. To configure the client for writing, calls the `getWriteApi()`  with organization, bucket, timestamp precision, batch size, and default tags
   ```js
   const writeApi = influxDB.getWriteApi(org, bucket, 'ns', {
     batchSize: batchSize + 1,
     defaultTags: {clientId: id},
   })
   ```
3. To write a data point, calls the [`writeApi.writePoint(point)`](https://github.com/influxdata/influxdb-client-js/blob/d76b1fe8c4000d7614f44d696c964cc4492826c6/packages/core/src/impl/WriteApiImpl.ts#L256)
   client library function
4. Internally, `writeApi.writePoint(point)` converts each new point to
   [line protocol]() and adds the line to an array in a `WriteBuffer` object.
5. Calls the [`writeApi.flush()`]() client library function.
6. Internally, `writeApi.flush()` calls the `writeApi.sendBatch()`](https://github.com/influxdata/influxdb-client-js/blob/d76b1fe8c4000d7614f44d696c964cc4492826c6/packages/core/src/impl/WriteApiImpl.ts#L147)
   client library function to write the points in batches to the `/api/v2/write` InfluxDB API endpoint.


#### Example: batch and write points

```python

```


### IoT Center: device dashboard

#### Example: query virtual device data with Flux

IoT Center uses the following Flux query to retrieve `environment` measurements:

```js
import "influxdata/influxdb/v1"    
from(bucket: "iot_center")
 |> range(start: ${fluxDuration(timeStart)})
 |> filter(fn: (r) => r._measurement == "environment")
 |> filter(fn: (r) => r["_field"] == "Temperature" or r["_field"] == "TVOC" or r["_field"] == "Pressure" or r["_field"] == "Humidity" or r["_field"] == "CO2")
 |> filter(fn: (r) => r.clientId == "virtual_device")
 |> v1.fieldsAsCols()
```

#### Query result sample

The query returns virtual device `environment` measurements that contain
any of the fields **Temperature**, **TVOC**, **Pressure**, **Humidity**, or **CO2**.

_measurement  |  _start  |  _stop  |  _time  |  clientId  |  CO2  |  CO2Sensor  |  GPSSensor  |  Humidity  |  HumiditySensor  |  Pressure  |  PressureSensor  |  Temperature  |  TemperatureSensor  |  TVOC  |  TVOCSensor |
| environment | 2022-02-08T22:38:31.329Z | 2022-02-15T22:38:31.329Z | 2022-02-08T22:39:00.000Z | virtual_device | 865 | virtual_CO2Sensor | virtual_GPSSensor | 32 | virtual_HumiditySensor | 980.1 | virtual_PressureSensor | 16.8 | virtual_TemperatureSensor | 564 | virtual_TVOCSensor |
| environment | 2022-02-08T22:38:31.329Z | 2022-02-15T22:38:31.329Z | 2022-02-08T22:40:00.000Z | virtual_device | 867 | virtual_CO2Sensor | virtual_GPSSensor | 31.8 | virtual_HumiditySensor | 980.3 | virtual_PressureSensor | 17.2 | virtual_TemperatureSensor | 565 | virtual_TVOCSensor |
| environment | 2022-02-08T22:38:31.329Z | 2022-02-15T22:38:31.329Z | 2022-02-08T22:41:00.000Z | virtual_device | 869 | virtual_CO2Sensor | virtual_GPSSensor | 31.4 | virtual_HumiditySensor | 980.3 | virtual_PressureSensor | 17 | virtual_TemperatureSensor | 565 | virtual_TVOCSensor |

### IoT device dashboard

IoT Center provides a dashboard of data visualizations for each registered device.
To view the device dashboard, on the "Virtual Device" page, click the
"Device Dashboard" button.
IoT Center UI `DashboardPage` executes the following steps to generate a dashboard visualization:
1. Calls the
[`getQueryApi(org)`]() client library function to configure the client for querying.
2. Calls the `queryTable(queryApi, query, options)` IoT Center function with the query configuration and the [Flux]() query
3. Returns a Promise that resolves with query result data as a [Giraffe Table interface](https://github.com/influxdata/giraffe/).

