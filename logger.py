#!/usr/bin/python -p

# import some basic libs
import time
import sys
import datetime

# import InfluxDB client
from influxdb import InfluxDBClient

# import our own libs
from config import load_config, load_measurements
from loxone import loxclient

# Initialize logging
import logging
lg = logging.getLogger(__name__)
logging.basicConfig(
    # filename=args.log_file,
    format='%(asctime)s %(threadName)s [%(levelname)s] %(name)s %(message)s',
    level=logging.DEBUG
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

# Create the InfluxDB object
client = InfluxDBClient(host, port, user, password, dbname)

if __name__ == '__main__':
    #from timeit import Timer
    #t_urllib2 = Timer("get_url2()", "from __main__ import get_url2")
    #print 'urllib2: {0}'.format(t_urllib2.timeit(number=1))
exit

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
            client.write_points(json_body)
        # Wait for next sample
        # time.sleep(interval)
        wait(60)

except KeyboardInterrupt:
    pass
