#!/usr/bin/env python3
import sys
import requests
from pprint import pprint
from influxdb import InfluxDBClient
import time
import os
import logging
from datetime import datetime, timezone

HELIALUX_SPECTRUM_IP=os.getenv("HELIALUX_SPECTRUM_IP")
MEASUREMENT = os.getenv("INFLUXDB_MEASUREMENT")
TIMEZONE = "Z"
LOGLEVEL = os.getenv("LOGLEVEL", "INFO")


logging.basicConfig(level=LOGLEVEL.upper())


def boolean_env_is_true(env):
    return os.getenv(env, "false").lower() == "true"


def main():
    influxdb_client = InfluxDBClient(
        host=os.getenv("INFLUXDB_HOST"),
        port=int(os.getenv("INFLUXDB_PORT", "8086")),
        username=os.getenv("INFLUXDB_USER"),
        password=os.getenv("INFLUXDB_PASSWORD"),
        database=os.getenv("INFLUXDB_DB"),
        ssl=boolean_env_is_true("INFLUXDB_SSL"),
        verify_ssl=not boolean_env_is_true("INFLUXDB_NO_VERIFY_SSL"),
    )

    while True:
        logging.debug("Loading new data…")

        r = requests.post(f"http://{HELIALUX_SPECTRUM_IP}/stat", data={"action": "10"})
        r.raise_for_status()

        data = r.json()
        led_state = data["C"]["ch"]

        logging.debug(
            f"Received white: {led_state[0]}, blue: {led_state[1]}, green: {led_state[2]}, red: {led_state[3]}"
        )

        point = {
            "time": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            "measurement": MEASUREMENT,
            "tags": {"device": "helialux-spectrum"},
            "fields": {
                "white": led_state[0],
                "blue": led_state[1],
                "green": led_state[2],
                "red": led_state[3],
            }
        }

        influxdb_client.write_points([point])

        time.sleep(30)


if __name__ == "__main__":
    main()
