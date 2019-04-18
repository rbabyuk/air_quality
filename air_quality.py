#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import time
import logging
from BME280 import *
from influxdb import InfluxDBClient

# Logging config
pathname = os.path.dirname(sys.argv[0])        
log_file = os.path.join(os.path.abspath(pathname), 'air_quality.log')
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(filename=log_file,level=logging.INFO,format=FORMAT)

# Settings
temperature_unit = 'C' # 'C' | 'F'
pressure_unit = 'mm Hg' # 'Pa' | 'mm Hg'
humidity_unit = '%'
temperature_field = 'temperature'
pressure_field = 'pressure'
humidity_field = 'humidity'

units = {temperature_field: temperature_unit, pressure_field: pressure_unit, humidity_field: humidity_unit}

def convert(value, unit):
        if unit == 'F':
                # Convert from Celsius to Fahrenheit
                return round(1.8 * value + 32.0, 2)
        if unit == 'mm Hg':
                 #Convert from Pa to mm Hg
                return round(value * 0.00750061683, 2)
        return value

#Read data from Sensor
ps = BME280()
ps_data = ps.get_data()

dataDict = {}
dataDict.setdefault("temperature", convert(ps_data['t'], units[temperature_field]))
dataDict.setdefault("humidity", convert(ps_data['h'], units[humidity_field]))
dataDict.setdefault("pressure", convert(ps_data['p'], units[pressure_field]))
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
influxClient = InfluxDBClient(host='localhost', port=8086, database='airquality')
#influxClient.create_database('airquality')
#print(influxClient.get_list_database())

now = time.asctime( time.gmtime(time.time()) )
# in case some of values are wrong the only you can do is to overwrite these specific series
#now = time.asctime( time.gmtime(1555343041) )
bodyDict = []
for key, value in dataDict.items():
    tmpDict = {}
    tmpDict.setdefault("time", now)
    tmpDict.setdefault("measurement", key)
    tmpDict.setdefault("fields", {}).setdefault("value", value)
    bodyDict.append(tmpDict)
    try:
        influxClient.write_points(bodyDict)
    except OSError as e:
       logging.error("Unable to write to InfluxDB: %s" % e)

#results = influxClient.query('SELECT "value" FROM "airquality"."autogen"."temperature"')
#print(results.raw)

