#!/usr/bin/env python3
# Usage: issNear.py [address]
# This program will turn on the blue LED if the ISS is within 1000 miles of the given address.
# From: https://codeclubprojects.org/en-GB/python/iss/
# pip install geopy
import gpiod
import json
import urllib.request
import time
import datetime
import threading

from geopy.geocoders import Nominatim
from geopy.distance  import geodesic

import sys

# calling the Nominatim tool and create Nominatim class
loc = Nominatim(user_agent="Geopy Library")

# Pass location on the command line
if len(sys.argv) > 1:
    address = sys.argv[1] 
else:
    address = "Brazil Indiana USA"
print("Looking up address: ", address)
getLoc = loc.geocode(address)
# Check if the address is valid
if getLoc is None:
    print(f"Error: Unable to find location for address '{address}'. Please provide a valid address.")
    sys.exit(1)  # Exit the program with an error code

print("Address found: ", getLoc.address)
city = (getLoc.latitude, getLoc.longitude)

url = 'http://api.open-notify.org/iss-now.json'

# Set up GPIO for blue LED
LED_CHIP = 'gpiochip1'
blue   = 18 # 'P9_19'
LED_LINE_OFFSET = [blue]
chip = gpiod.Chip(LED_CHIP)
lines = chip.get_lines(LED_LINE_OFFSET)
lines.request(consumer='blue.py', type=gpiod.LINE_REQ_DIR_OUT)

# Turn on blue LED
print("blue LED on")
lines.set_values([1])     # blue LED on

# Function to check if it's nighttime
def is_nighttime():
    current_time = datetime.datetime.now().time()
    # Define nighttime as between 11:00 PM and 5:00 AM
    night_start = datetime.time(23, 0)  # 11:00 PM
    night_end = datetime.time(5, 0)    # 5:00 AM

    # Check if the current time is within the nighttime range
    return current_time >= night_start or current_time <= night_end

# Global variable to control the blinking thread
blinking = False
fast     = False    # Function to blink the LED fast

def blink_led():
    global blinking, fast

    while blinking:
        lines.set_values([1])  # Turn on LED
        time.sleep(0.2 if fast else 1)  # Faster blink if fast=True
        lines.set_values([0])  # Turn off LED
        time.sleep(0.2 if fast else 1)  # Faster blink if fast=True

def control_led_based_on_distance():
    global blinking, fast
    
    try:
        # Check if it's nighttime
        if is_nighttime():
            # print("It's nighttime. Turning off the LED.")
            blinking = False  # Stop blinking
            lines.set_values([0])  # Turn off LED
            return
        
        # Get the current location of the ISS
        response = urllib.request.urlopen(url)
        result = json.loads(response.read())
        # print(result)

        location = result['iss_position']
        iss = (float(location['latitude']), float(location['longitude']))
        print('Current Location : ', iss)

        # Get the distance from the ISS to city
        # geodesic returns distance in miles between two points
        distance = geodesic(iss, city).miles
        # distance = 400  # For testing

        cleaned_address = getLoc.address.replace(", United States", "").strip()
        print('Distance from ISS to ', cleaned_address, ':', 
              int(distance), 'miles, ', int(distance*1.60934), 'km')

        # Check the distance and control the LED
        if distance < 750:
            print("Distance < 750 miles")
            fast = True  # Set fast blinking
            if not blinking:
                blinking = True
                threading.Thread(target=blink_led, daemon=True).start()
        elif distance < 1500:
            print("Distance < 1500 miles")
            fast = False
            if not blinking:
                blinking = True
                threading.Thread(target=blink_led, daemon=True).start()
        elif distance < 2500:
            blinking = False  # Stop blinking
            print("Distance < 2500 miles")  # On steady
            lines.set_values([1])
        else:
            blinking = False  # Stop blinking
            print("Distance > 2500 miles")
            lines.set_values([0])

    except Exception as err:
        print('ERROR:', err)

# Main loop
while True:
    control_led_based_on_distance()
    time.sleep(60)  # Wait for 60 seconds before checking again
