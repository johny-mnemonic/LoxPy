#!/usr/bin/python -p

# import some basic libs
import time
import sys
import datetime
import argparse

# import InfluxDB client
from influxdb import InfluxDBClient

# import our own libs
from config import load_config, load_measurements
from loxone import loxclient

parser = argparse.ArgumentParser(description="Logger script for getting stats from Miniserver to InfluxDB")
parser.add_argument("-v", "--verbose", action = "store_true",
                    help="Enable verbose output")
parser.add_argument("-d", "--debug", action = "store_true",
                    help="Enable debug output")
# Allow user to set session and run number via args otherwise auto-generate
parser.add_argument("-s", "--session", default = "dev",
                    help="Logging session. Default is ''dev'")
parser.add_argument("-r", "--run", default = None,
                    help="Run number. Default is generated from datetime.now()")
parser.add_argument("-l", "--lib", default = "requests",
                    help="Http library. Default is 'requests'")
args = parser.parse_args()

# Initialize logging
import logging
lg = logging.getLogger(__name__)
if args.verbose:
    #print("Verbose output turned on")
    loglvl = logging.INFO
elif args.debug:
    #print("Debug output turned on")
    loglvl = logging.DEBUG
else:
    loglvl = logging.ERROR
logging.basicConfig(
    # filename=args.log_file,
    format='%(asctime)s %(threadName)s [%(levelname)s] %(name)s %(message)s',
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


def wait(n):
    '''Wait until the next increment of n seconds'''
    x = time.time()
    lg.debug("It is {0} now, will wait {1}s with next execution".format(time.asctime(), n - (x % n)))
    time.sleep(n - (x % n))

def get_measurements():
    measurements = {}
    # Get all measurements from Miniserver
    for loxobject in load_measurements('measurements.txt'):
        loxval = loxclient(loxhost, loxusr, loxpass, obj=loxobject, strip=True, lib=args.lib)
        if loxval is None:
            lg.error("Getting of value for {} failed.".format(loxobject))
            continue
        measurements[loxobject] = loxval
        lg.info("{0} = {1}".format(loxobject, loxval))
        lg.debug("Print measurements: {}".format(measurements))
    lg.info("Print measurements: {}".format(measurements))
    return measurements


# Allow user to set session and run number via args otherwise auto-generate
# TODO remove this section once we get out of alfa testing stage
if args.run == None:
    now = datetime.datetime.now()
    runNo = now.strftime("%Y%m%d%H%M")
lg.debug("Session: {}".format(args.session))
lg.debug("runNo: {}".format(runNo))

#if len(sys.argv) > 1:
    #if (len(sys.argv) < 3):
        #print("Must define session and run number!!")
        #sys.exit()
    #else:
        #session = sys.argv[1]
        #runNo = sys.argv[2]
#else:
    #session = "dev"
    #now = datetime.datetime.now()
    #runNo = now.strftime("%Y%m%d%H%M")

#lg.debug("Session: {}".format(session))
#lg.debug("runNo: {}".format(runNo))

# Create the InfluxDB object
client = InfluxDBClient(host, port, user, password, dbname)

if __name__ == '__main__':
    from timeit import Timer
    t_collect = Timer("get_measurements()", "from __main__ import get_measurements")
    print 'Get all measurements: {0}'.format(t_collect.timeit(number=1))
    exit(0)

# Run until keyboard out
try:
    while True:
        iso = time.ctime()
        measurements = {}
        # Get all measurements from Miniserver
        for loxobject in load_measurements('measurements.txt'):
            loxval = loxclient(loxhost, loxusr, loxpass, obj=loxobject, strip=True)
            if loxval is None:
                lg.error("Getting of value for {} failed.".format(loxobject))
                continue
            measurements[loxobject] = loxval
        if measurements == {}:
            lg.error("We didn't receive any values from Miniserver. Not going to push anything to InfluxDB.")
        else:
            lg.debug("Obtained measurements: {}".format(measurements))
            json_body = [
                {
                    "measurement":
                        session,
                        "tags": {"run": runNo},
                        "time": iso,
                        "fields": measurements
                  }
                ]

            # Write JSON to InfluxDB
            lg.debug("The write json content is: {}".format(json_body))
            #client.write_points(json_body)
        # Wait for next sample
        # time.sleep(interval)
        wait(60)

except KeyboardInterrupt:
    pass
