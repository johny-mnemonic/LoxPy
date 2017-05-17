#!/usr/bin/python

# import libs for logging
import time
import sys
import datetime
import logging

# import InfluxDB client
from influxdb import InfluxDBClient

# import libs for Loxone connection
import requests
from requests.auth import HTTPBasicAuth
import json

# import our own libs
import config

# Initialize logging
lg = logging.getLogger(__name__)
logging.basicConfig(
    #filename=args.log_file,
    format='%(asctime)s %(threadName)s [%(levelname)s] %(name)s %(message)s',
    level=logging.DEBUG
    )

# Read configuration from config file
config_cache=config.load_config(input_file="secrets.yml")
host = config_cache["influxdb::host"]
port = config_cache["influxdb::port"]
dbname = config_cache["influxdb::db"]
user = config_cache["influxdb::user"]
password = config_cache["influxdb::password"]
loxusr = config_cache["loxone::user"]
loxpass = config_cache["loxone::password"]
loxhost = config_cache["loxone::host"]

# Sample period (s)
interval = 60

# Allow user to set session and run number via args otherwise auto-generate
# TODO remove this section once we get out of alfa testing stage
if len(sys.argv) > 1:
    if (len(sys.argv) < 3):
        print("Must define session and run number!!")
        sys.exit()
    else:
        session = sys.argv[1]
        runNo = sys.argv[2]
else:
    session = "dev"
    now = datetime.datetime.now()
    runNo = now.strftime("%Y%m%d%H%M")

lg.debug("Session: {}".format(session))
lg.debug("runNo: {}".format(runNo))

# Set Loxone URL
url = "http://{0}/jdev/sps/io/LightSensor_Pracovna/state".format(loxhost)

# Create the InfluxDB object
client = InfluxDBClient(host, port, user, password, dbname)

# Run until keyboard out
try:
    while True:
        myResponse = requests.get(url, auth=HTTPBasicAuth(loxusr, loxpass), verify=True)
        if (myResponse.ok):
            jData = myResponse.json()
            lg.debug("The response json content is: {}".format(jData))
            lg.debug("The requested value is: {}".format(jData['LL']['value']))

            iso = time.ctime()
        else:
            myResponse.raise_for_status()

        json_body = [
            {
              "measurement": session,
                  "tags": {
                      "run": runNo,
                      },
                  "time": iso,
                  "fields": {
                      "LightSensor" : jData['LL']['value']
                  }
              }
            ]

        # Write JSON to InfluxDB
        lg.debug("The write json content is: {}".format(json_body))
        client.write_points(json_body)
        # Wait for next sample
        time.sleep(interval)

except KeyboardInterrupt:
    pass
