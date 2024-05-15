# iot-api-python

This example project provides a Python REST API server that interacts with the InfluxDB v2 HTTP API.
The project uses the [Flask](https://palletsprojects.com/p/flask/) framework and the [InfluxDB v2 API client library for Python](https://docs.influxdata.com/influxdb/v2/api-guide/client-libraries/python/) to demonstrate how to build an app that collects, stores, and queries IoT device data.
After you have set up and run your `iot-api-python` API server, you can consume the API using the [iot-api-ui](https://github.com/influxdata/iot-api-ui) standalone React frontend.

## Features

This application demonstrates how you can use InfluxDB client libraries to do the following:

- Create and manage InfluxDB authorizations (API tokens and permissions).
- Write and query device metadata in InfluxDB.
- Write and query telemetry data in InfluxDB.
- Generate data visualizations with the InfluxDB Giraffe library.

## Tutorial and support

To learn how to build this app from scratch, follow the [InfluxDB v2 OSS tutorial](https://docs.influxdata.com/influxdb/v2/api-guide/tutorials/python/) or [InfluxDB Cloud tutorial](https://docs.influxdata.com/influxdb/cloud/api-guide/tutorials/python/).
The app is an adaptation of [InfluxData IoT Center](https://github.com/bonitoo-io/iot-center-v2), simplified to accompany the IoT Starter tutorial.

For help, refer to the tutorials and InfluxDB documentation or use the following resources:

- [InfluxData Community](https://community.influxdata.com/)
- [InfluxDB Community Slack](https://influxdata.com/slack)

To report a problem, submit an issue to this repo or to the [`influxdata/docs-v2` repo](https://github.com/influxdata/docs-v2/issues).

## Get started

### Set up InfluxDB prerequisites

Follow the tutorial instructions to setup your InfluxDB organization, API token, and buckets:

- [Set up InfluxDB OSS v2 prerequisites](https://docs.influxdata.com/influxdb/v2/api-guide/tutorials/python/#set-up-influxdb)
- [Set up InfluxDB Cloud v2 prerequisites](https://docs.influxdata.com/influxdb/cloud/api-guide/tutorials/python/#set-up-influxdb)

Next, [clone and run the API server](#clone-and-run-the-api-server).

### Clone and run the API server

1. Clone this repository to your machine.
2. Change to the directory--for example, enter the following command in your terminal:

   ```bash
   cd ./iot-api-python
   ```

3. Set environment variables for `INFLUX_TOKEN` and `INFLUX_ORG`--for example, enter the following commands in your terminal:

   ```bash
   export INFLUX_TOKEN=<INFLUX_TOKEN>
   export INFLUX_ORG=<INFLUX_ORG_ID>
   ```

   Replace the following:

   - **`<INFLUX_TOKEN>`**: your InfluxDB [API token](#authorization) with permission to query (_read_) buckets and create (_write_) authorizations for devices.
   - **`<INFLUX_ORG_ID>`**: your InfluxDB organization ID.

4. If you need to adjust the default URL or bucket names to match your InfluxDB instance, edit the settings in`./config.ini`:

   ```ini
   [APP]
   INFLUX_URL = <INFLUX_URL>
   INFLUX_BUCKET = iot_center
   INFLUX_BUCKET_AUTH = iot_center_devices
   ```

   Replace the following:

   - **`<INFLUX_URL>`**: your InfluxDB instance URL--for example, the default OSS URL `http://localhost:8086`.

5. Create and activate a Python virtual environment for the project.
   Enter the following commands into your terminal:

   ```bash
   # Create a new virtual environment named "virtualenv"
   # Python 3.8+
   python -m venv virtualenv

   # Activate the virtualenv (OS X & Linux)
   source virtualenv/bin/activate
   ```

6. Install `pdm` package manager for your system.
On Linux or macOS, enter the following command in your terminal:

   ```bash
   curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -
   ```

   On Windows, enter the following command in your terminal:

   ```bash
   (Invoke-WebRequest -Uri https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py -UseBasicParsing).Content | python -
   ```

7. Use `pdm` to install dependencies.
   Enter the following command in your terminal:

   ```bash
   pdm install
   ```

8. If you use a bash terminal, you can set an environment variable to use dependencies in `pdm.lock` when you run your application scripts--for example, enter the following command in your bash terminal:

   ```bash
   eval "$(pdm --pep582)"
   ```

9. To start the Flask application, enter the following command in your terminal:

    ```bash
    flask run -h localhost -p 3001
    ```

    To view the application, visit <http://localhost:3001> in your browser.

10. _Optional_: Run the [iot-api-ui](https://github.com/influxdata/iot-api-ui) React frontend to interact with your IoT Starter API server.

## Troubleshoot

### Error: could not find bucket

```json
{"error":"failed to load data: HttpError: failed to initialize execute state: could not find bucket \"iot_center_devices\""}
```

Solution: [create buckets](#set-up-influxdb-prerequisites) or adjust the defaults in `config.ini` to match your InfluxDB instance.

## Learn More

### InfluxDB

- Develop with the InfluxDB API for [OSS v2](https://docs.influxdata.com/influxdb/v2/api-guide/) or [Cloud v2](https://docs.influxdata.com/influxdb/cloud/api-guide/).