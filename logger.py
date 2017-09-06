#!/usr/bin/python -p

# import some basic libs
import time
import sys
import datetime
import argparse
import textwrap
import logging

# import InfluxDB client
from influxdb import InfluxDBClient

# import our own libs
from config import load_config, load_measurements
from loxone import loxclient

parser = argparse.ArgumentParser(
    description="Logger script for getting stats from Miniserver to InfluxDB"
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Enable verbose output"
)
parser.add_argument(
    "-d", "--debug", action="store_true", help="Enable debug output"
)
parser.add_argument(
    "--dry", action="store_true", help=textwrap.dedent('''\
    Do not write to InfluxDB. Only get values from Miniserver."''')
)
# Allow user to set session and run number via args otherwise auto-generate
parser.add_argument(
    "-s", "--session", default="dev", help="Logging session. Default is ''dev'"
)
parser.add_argument(
    "-r", "--run", default=None,
    help="Run number. Default is generated from datetime.now()"
)
parser.add_argument(
    "-l", "--lib", default="requests",
    help="Http library. Default is 'requests'"
)
parser.add_argument(
    "-log", "--log-file", default=None,
    help="Log into specified file, instead of stdout"
)
args = parser.parse_args()

# Initialize logging
lg = logging.getLogger(__name__)
log_format='%(asctime)s %(threadName)s [%(levelname)s] %(name)s %(message)s'
if args.verbose:
    #print("Verbose output turned on")
    loglvl = logging.INFO
elif args.debug:
    #print("Debug output turned on")
    loglvl = logging.DEBUG
else:
    loglvl = logging.ERROR
if args.log_file is None:
    logging.basicConfig(
        format=log_format,
        level=loglvl
        )
else:
    logging.basicConfig(
        filename=args.log_file,
        format=log_format,
        level=loglvl
        )

# Read configuration from config file
config_cache = load_config(input_file="secrets.yml")
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
if args.run is None:
    now = datetime.datetime.now()
    runNo = now.strftime("%Y%m%d%H%M")
else:
    runNo = args.run
session = args.session
lg.debug("Session: {}".format(args.session))
lg.debug("Run number: {}".format(runNo))


def wait(n):
    '''Wait until the next increment of n seconds'''
    x = time.time()
    lg.debug("It is {0} now, \
    will wait {1}s with next execution".format(time.asctime(), n - (x % n)))
    time.sleep(n - (x % n))


def get_measurements():
    measurements = {}
    # Get all measurements from Miniserver
    lg.info("Getting measurements from Miniserver...")
    for loxobject in load_measurements('measurements.txt'):
        loxval = loxclient(
            loxhost, loxusr, loxpass, obj=loxobject, strip=True, lib=args.lib
        )
        if loxval is None:
            lg.error("Getting of value for {} failed.".format(loxobject))
            continue
        measurements[loxobject] = loxval
        lg.debug("{0} = {1}".format(loxobject, loxval))
        #lg.debug("Obtained measurements: {}".format(measurements))
    lg.info("Obtained measurements: {}".format(measurements))
    return measurements

# Create the InfluxDB object
client = InfluxDBClient(host, port, user, password, dbname)


def write_measurements(data):
    json_body = [
        {
            "measurement":
                session,
                "tags": {"run": runNo},
                "time": iso,
                "fields": data
        }
    ]

    # Write JSON to InfluxDB
    lg.debug("The write json content is: {}".format(json_body))
    client.write_points(json_body)

if args.dry:
    from timeit import Timer
    t_collect = Timer(
        "get_measurements()", "from __main__ import get_measurements"
    )
    print(
        'Time to get all measurements: {0}'.format(t_collect.timeit(number=1))
    )
    exit(0)

# Run until keyboard out
try:
    while True:
        iso = time.ctime()
        measurements = get_measurements()
        if measurements == {}:
            lg.error("We didn't receive any values from Miniserver. \
            Not going to push anything to InfluxDB.")
        else:
            write_measurements(measurements)
        # Wait for next sample
        wait(interval)

except KeyboardInterrupt:
    pass
