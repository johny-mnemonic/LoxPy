#!/usr/bin/python

import config

import argparse
import requests
from requests.auth import HTTPBasicAuth
import json
from string import Template

parser = argparse.ArgumentParser(description="Simple Loxone RESTful client. Without paramteres it checks Miniserver state")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Enable verbose output")
parser.add_argument("-d", "--debug", action="store_true",
                    help="Enable debug output")
parser.add_argument("-o", "--object",
                    help="Loxone object to query. Could be name or UUID")
parser.add_argument("-a", "--action", default='state',
                    help="Action to do with the object. Default is 'state'")
args = parser.parse_args()
#if args.verbose:
#    print("Verbose output turned on")

# Read configuration from config file
config_cache=config.load_config(input_file="secrets.yml")
loxusr = config_cache["loxone::user"]
loxpass = config_cache["loxone::password"]
loxhost = config_cache["loxone::host"]

#args.object = "LightSensor_Pracovna"

if args.object == None:
  url = 'http://loxone/jdev/sps/state'
else:
  url = 'http://' + loxhost + '/jdev/sps/io/' + args.object + '/' + args.action

# It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
#myResponse = requests.get(url,auth=HTTPBasicAuth(raw_input("username: "), raw_input("Password: ")), verify=True)
myResponse = requests.get(url, auth=HTTPBasicAuth(loxusr,loxpass), verify=True)
if args.debug:
  print('Http return code is: {0}'.format(myResponse.status_code))

# For successful API call, response code will be 200 (OK)
if (myResponse.ok):
  jData = myResponse.json()
  if args.debug:
    print("The response raw content is:")
    print(myResponse.text)
    #print("\n")
    print("The response json contains {0} properties".format(len(jData)))
    #print("\n")
    print("The response json content is:")
    print(jData)
    #print("\n")
  if args.object == None and args.action == 'state':
    if jData['LL']['value'] == '1':
      print("Miniserver is booting")
    elif jData['LL']['value'] == '2':
      print("Miniserver has loaded the program")
    elif jData['LL']['value'] == '3':
      print("Miniserver has started")
    elif jData['LL']['value'] == '4':
      print("Loxone link has started")
    elif jData['LL']['value'] == '5':
      print("Miniserver is running")
    elif jData['LL']['value'] == '6':
      print("Miniserver state is changing")
    elif jData['LL']['value'] == '7':
      print("Miniserver is in error state")
    elif jData['LL']['value'] == '8':
      print("Miniserver is updating")
  elif args.verbose or args.debug:
    print("Value of {} is {} ".format(args.object,jData['LL']['value']))
  else:
    print(jData['LL']['value'])

else:
  # If response code is not ok (200), print the resulting http error code with description
  myResponse.raise_for_status()
