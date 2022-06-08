#iot-api-python

This project is an example Flask and React application that uses the InfluxDB API client library for Python.
The application is an adaptation of [InfluxData IoT Center](https://github.com/bonitoo-io/iot-center-v2), intentionally simplified to accompany the InfluxData IoT Starter tutorial.

## Features

This application demonstrates how you can use InfluxDB client libraries to do the following:

- Create and manage InfluxDB authorizations (API tokens and permissions).
- Write and query device metadata in InfluxDB.
- Write and query telemetry data in InfluxDB.
- Generate data visualizations with the InfluxDB UI libraries.

## Get started

### Clone this project

To clone the repo and change to the project directory,
enter the following commands into your terminal:

```bash
git@github.com:influxdata/iot-api-python.git
cd iot-api-python
```

### Set up InfluxDB

1. If you don't already have an InfluxDB instance, [create an InfluxDB Cloud account](https://www.influxdata.com/products/influxdb-cloud/) or [install InfluxDB OSS](https://www.influxdata.com/products/influxdb/).

2. Set environment variables for `INFLUX_TOKEN` and `INFLUX_ORG`

   ```bash
   export INFLUX_TOKEN=<INFLUX_TOKEN>
   export INFLUX_ORG=<INFLUX_ORG_ID>
   ```

   - **`<INFLUX_TOKEN>`**: your InfluxDB [API token](#authorization) with permission to query (_read_) buckets and create (_write_) authorizations for devices.
   - **`<INFLUX_ORG_ID>`**: your InfluxDB organization ID.

3. If you need to adjust the defaults to match your InfluxDB instance, edit the settings in`./config.ini`:

   ```ini
   [APP]
   INFLUX_URL = http://localhost:8086
   INFLUX_BUCKET = iot_center
   INFLUX_BUCKET_AUTH = iot_center_devices
   ```

   Replace the following:

   - **`<INFLUX_URL>`**: your InfluxDB instance URL.

### Install and activate the Python environment

Create and activate a Python virtual environment for the new project.

```bash
# Create a new virtual environment named "virtualenv"
# Python 3.8+
python -m venv virtualenv

# Activate the virtualenv (OS X & Linux)
source virtualenv/bin/activate
```

### Install PDM package manager

`pdm` is a modern package manager for Python that manages dependencies for your application.
To install `pdm` for Linux or macOS, enter the following command into your terminal:

```bash
curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -
For Windows
```

To install `pdm` for Windows, enter the following command into your terminal:

```bash
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py -UseBasicParsing).Content | python -
```

### Install dependencies

Use `pdm` to install the dependencies listed in `pdm.lock`.
Enter the following command into your terminal:

```bash
pdm install
```

### Set the PDM environment

Set your environment to use the dependencies in `pdm.lock` when you run your application scripts.
For bash terminals, you can set an environment variable to enable **PEP 582** support.
To set the environment variable, enter the following command into your terminal:

```bash
eval "$(pdm --pep582)"
```

### Run the application

To start the Flask application, enter the following command into your terminal:

```bash
flask run -h localhost -p 5200
```

To view the application, visit <http://localhost:5200> in your browser.
