#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import sys
import time

from influxdb import InfluxDBClient

from BME280 import BME280


def convert(value, unit):
    if unit == 'F':
        # Convert from Celsius to Fahrenheit
        return round(1.8 * value + 32.0, 2)
    if unit == 'mm Hg':
        # Convert from Pa to mm Hg
        return round(value * 0.00750061683, 2)
    return value


def air_calc():
    # Logging config
    pathname = os.path.dirname(sys.argv[0])
    log_file = os.path.join(os.path.abspath(pathname), 'air_quality.log')
    format_ = '%(asctime)-15s %(levelname)s %(message)s'
    logging.basicConfig(filename=log_file, level=logging.INFO, format=format_)

    # Settings
    temperature_unit = 'C'  # 'C' | 'F'
    pressure_unit = 'mm Hg'  # 'Pa' | 'mm Hg'
    humidity_unit = '%'
    temperature_field = 'temperature'
    pressure_field = 'pressure'
    humidity_field = 'humidity'

    units = {temperature_field: temperature_unit, pressure_field: pressure_unit, humidity_field: humidity_unit}

    # Read data from Sensor
    ps = BME280()
    ps_data = ps.get_data()

    data_dict = {}
    data_dict.setdefault("temperature", convert(ps_data['t'], units[temperature_field]))
    data_dict.setdefault("humidity", convert(ps_data['h'], units[humidity_field]))
    data_dict.setdefault("pressure", convert(ps_data['p'], units[pressure_field]))
    # example of data structure
    """
    json_body = [
        {
            "measurement": "cpu_load_short",
            "tags": {
                "host": "server01",
                "region": "us-west"
            },
            "time": "2009-11-10T23:00:00Z",
            "fields": {
                "value": 0.64
            }
        }
    ]
    """
    influx_client = InfluxDBClient(host='localhost', port=8086, database='airquality')
    # influxClient.create_database('airquality')
    # print(influxClient.get_list_database())

    now = time.asctime(time.gmtime(time.time()))
    # in case some of values are wrong the only you can do is to overwrite these specific series
    # now = time.asctime( time.gmtime(1555343041) )
    body_dict = []
    for key, value in data_dict.items():
        tmp_dict = {}
        tmp_dict.setdefault("time", now)
        tmp_dict.setdefault("measurement", key)
        tmp_dict.setdefault("fields", {}).setdefault("value", value)
        body_dict.append(tmp_dict)
        try:
            influx_client.write_points(body_dict)
        except OSError as e:
           logging.error("Unable to write to InfluxDB: %s" % e)

    # results = influxClient.query('SELECT "value" FROM "airquality"."autogen"."temperature"')
    # print(results.raw)


if __name__ == '__main__':
    air_calc()
