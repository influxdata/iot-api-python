# iot-api-python

This example project provides a Python server-side REST API that interacts with InfluxDB.
It is an adaptation of [InfluxData IoT Center](https://github.com/bonitoo-io/iot-center-v2), simplified to accompany the InfluxData IoT Starter tutorial.
You can consume this API with the example [iot-api-ui](https://github.com/influxdata/iot-api-ui) React frontend.
The project uses the [Flask](https://palletsprojects.com/p/flask/) framework and the InfluxDB API client library for Python.

## Features

This application demonstrates how you can use InfluxDB client libraries to do the following:

- Create and manage InfluxDB authorizations (API tokens and permissions).
- Write and query device metadata in InfluxDB.
- Write and query telemetry data in InfluxDB.
- Generate data visualizations with the InfluxDB Giraffe library.

## Get started

To learn how to create the app from scratch, follow the IoT Starter tutorial.
To run the app, do the following:

1. If you haven't already, [create an InfluxDB Cloud account](https://www.influxdata.com/products/influxdb-cloud/) or [install InfluxDB OSS](https://www.influxdata.com/products/influxdb/).
2. Clone this repository to your machine.
3. Change to the directory--for example, enter the following code into the terminal:

   ```bash
   cd ./iot-api-python
   ```

4. Set environment variables for `INFLUX_TOKEN` and `INFLUX_ORG`--for example, enter the following commands into your terminal:

   ```bash
   export INFLUX_TOKEN=<INFLUX_TOKEN>
   export INFLUX_ORG=<INFLUX_ORG_ID>
   ```

   Replace the following:

   - **`<INFLUX_TOKEN>`**: your InfluxDB [API token](#authorization) with permission to query (_read_) buckets and create (_write_) authorizations for devices.
   - **`<INFLUX_ORG_ID>`**: your InfluxDB organization ID.

5. If you need to adjust the defaults to match your InfluxDB instance, edit the settings in`./config.ini`:

   ```ini
   [APP]
   INFLUX_URL = <INFLUX_URL>
   INFLUX_BUCKET = iot_center
   INFLUX_BUCKET_AUTH = iot_center_devices
   ```

   Replace the following:

   - **`<INFLUX_URL>`**: your InfluxDB instance URL--for example, the default OSS URL `http://localhost:8086`.

6. Create and activate a Python virtual environment for the project.
   Enter the following commands into your terminal:

   ```bash
   # Create a new virtual environment named "virtualenv"
   # Python 3.8+
   python -m venv virtualenv

   # Activate the virtualenv (OS X & Linux)
   source virtualenv/bin/activate
   ```

7. Install `pdm` package manager for your system.
On Linux or macOS, enter the following command into your terminal:

   ```bash
   curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -
   ```

   On Windows, enter the following command into your terminal:

   ```bash
   (Invoke-WebRequest -Uri https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py -UseBasicParsing).Content | python -
   ```

8. Use `pdm` to install dependencies.
   Enter the following command into your terminal:

   ```bash
   pdm install
   ```

9. If you use a bash terminal, you can set an environment variable to use dependencies in `pdm.lock` when you run your application scripts.
   Enter the following command into your bash terminal:

   ```bash
   eval "$(pdm --pep582)"
   ```

10. To start the Flask application, enter the following command into your terminal:

    ```bash
    flask run -h localhost -p 3001
    ```

    To view the application, visit <http://localhost:3001> in your browser.
11. Next, you can use the example [iot-api-ui](https://github.com/influxdata/iot-api-ui) React frontend to interact with the API.
