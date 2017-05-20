# LoxPy
My first Python endeavour

First goal is to get statistics data from Loxone Miniserver to InfluxDB and visualize it with Grafana.
As I am not a programmer and I have never written anything in Python, it won't look nice at the beginning, but I will improve...hopefully ;-)

Repo content:
loxone.py  - This is simple Loxone client library, that works on one Loxone object. By default it gets it's state.
logger.py - This serves as a daemon to read values from Loxone and feeds them into InfluxDB

Two config files are ommited:
measurements.txt - simple text file containing Loxone object names. One per line.
secrets.yml - yaml file containing credentials and other connection parameters. Check code above for expected variables.
