#!/usr/bin/python

import config
import argparse
import getpass

from loxone import loxclient

parser = argparse.ArgumentParser(description="Simple Loxone RESTful client. Without paramteres it checks Miniserver state")
parser.add_argument("-v", "--verbose", action = "store_true",
                    help="Enable verbose output")
parser.add_argument("-d", "--debug", action = "store_true",
                    help="Enable debug output")
parser.add_argument("-o", "--object",
                    help="Loxone object to query. Could be name or UUID")
parser.add_argument("-a", "--action", default = 'state',
                    help="Action to do with the object. Default is 'state'. You can send 'On', 'Off' or 'pulse' (to simulate click).")
parser.add_argument("-u", "--user", default = None,
                    help="Loxone user to use instead of the one in config file. Will ask for password.")
parser.add_argument("-p", "--password", default = None,
                    help="Loxone user password")
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
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s',
    level=loglvl
    )

# Read configuration from config file
config_cache=config.load_config(input_file="secrets.yml")
loxhost = config_cache["loxone::host"]

# Override credentials if specified by user
if args.user is None:
    loxusr = config_cache["loxone::user"]
    loxpass = config_cache["loxone::password"]
else:
    loxusr = args.user
    if args.password is None:
        loxpass = getpass.getpass()
    else:
        loxpass = args.password

# debug default
#args.object = "LightSensor_Pracovna"

lg.debug("Calling loxclient action '{0}' for '{1}'".format(args.action, args.object))
value = loxclient(loxhost, loxusr, loxpass, args.action, args.object)
if value == None:
    lg.error("Miniserver connection failed or returned no data")
    exit(1)

if args.object == None and args.action == 'state':
    if value == '1':
        print("Miniserver is booting")
    elif value == '2':
        print("Miniserver has loaded the program")
    elif value == '3':
        print("Miniserver has started")
    elif value == '4':
        print("Loxone link has started")
    elif value == '5':
        print("Miniserver is running")
    elif value == '6':
        print("Miniserver state is changing")
    elif value == '7':
        print("Miniserver is in error state")
    elif value == '8':
        print("Miniserver is updating")
elif args.verbose or args.debug:
    lg.info("Value of {} is {} ".format(args.object,value))
else:
    print(value)
