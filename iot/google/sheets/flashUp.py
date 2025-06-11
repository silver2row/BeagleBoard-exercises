#!/usr/bin/env python3
# Pings google and turns on a RGB light according to the response time.

import gpiod
import subprocess
import time
import re
import datetime as dt
import logging
import os
import signal
import sys
from logging.handlers import RotatingFileHandler

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flashup.log')
# Create rotating file handler with max size of 1MB and 5 backup files
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=1024*1024,  # 1MB
    backupCount=5,
    encoding='utf-8'
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        file_handler,
        logging.StreamHandler()  # This will maintain console output
    ]
)
logger = logging.getLogger(__name__)
logger.info('Logging initialized. Log file: %s (with rotation)', log_file)

pingCmd = ["ping", "-w1", "www.google.com"]
p = re.compile('time=[0-9.]*')      # We'll search for time= followed by digits and .
ms = 15000          # Repeat time in ms.
thresh = 40.0      # If time is above this, turn on warning light
hist = 10* [thresh]  # Keep track of the last 10 values
current = 0        # Insert next value here 

LED_CHIP = 'gpiochip0'
red   = 30 # 'P9_11'
green =  5 # 'P9_17'
blue  = 31 # 'P9_13'
LED_LINE_OFFSET = [red, green, blue]

chip = gpiod.Chip(LED_CHIP)
lines = chip.get_lines(LED_LINE_OFFSET)
lines.request(consumer='flashup.py', type=gpiod.LINE_REQ_DIR_OUT)

def is_nighttime():
    """Check if current time is outside operating hours (5:00-21:00)"""
    hour = dt.datetime.now().hour
    return hour <= 5 or hour >= 21

# Turn all LEDs off
def allOff():
    logger.info("Turning all LEDs off")
    lines.set_values([0, 0, 0])  # All off

def cleanup(signum, frame):
    """Handle cleanup when script is interrupted"""
    logger.info("Received interrupt signal %d. Cleaning up...", signum)
    allOff()
    logger.info("Cleanup complete. Exiting.")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, cleanup)  # Ctrl+C
signal.signal(signal.SIGTERM, cleanup)  # kill command

lines.set_values([1, 0, 1])     # red and blue
logger.info("Starting ping monitoring")

try:
    while True:
        if is_nighttime():
            logger.info('Outside operating hours (5:00-21:00), turning off LEDs')
            allOff()
        else:
            try:
                # returns output as byte string
                returned_output = subprocess.check_output(pingCmd, stderr=subprocess.STDOUT).decode("utf-8")
                
                timems = float(p.search(returned_output).group()[5:])
                average = sum(hist)/len(hist)
                hist[current] = timems
                current = current + 1
                if current >= len(hist):
                    current=0
                logger.info('Ping: time = %5.2f, average = %5.2f' % (timems, average))
                
                if timems > 1.1*average:
                    logger.warning('High latency detected: %5.2f ms (avg: %5.2f ms)', timems, average)
                    lines.set_values([1, 1, 0])     # red and green
                else:
                    lines.set_values([0, 1, 0])     # green

                    
            except subprocess.CalledProcessError as err:
                logger.error('Ping failed: %s', err)
                lines.set_values([1, 0, 0])#        # red

        time.sleep(ms/1000)

except Exception as e:
    logger.error("Unexpected error: %s", str(e))
    cleanup(signal.SIGTERM, None)
