#!/usr/bin/env python
import time
import math
import sys
from LedStrip_WS2801 import LedStrip_WS2801

amp = 15
f = 25
shift = 3

def fillAll(ledStrip, color, sleep):
    for i in range(0, ledStrip.nLeds):
        ledStrip.setPixel(i, color)
    ledStrip.update()

def rainbow(ledStrip, nrOfleds):
    phase = 0
    while True:
        for i in range(0, nrOfleds):
            r = int((amp * (math.sin(2*math.pi*f*(i-phase-0*shift)/nrOfleds) + 1)) + 1)
            g = int((amp * (math.sin(2*math.pi*f*(i-phase-1*shift)/nrOfleds) + 1)) + 1)
            b = int((amp * (math.sin(2*math.pi*f*(i-phase-2*shift)/nrOfleds) + 1)) + 1)
            ledStrip.setPixel(i, [r, g, b])
    
        ledStrip.update()

        phase = phase + 1
        time.sleep(0.100)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        nrOfleds = 240
    else:
        nrOfleds = int(sys.argv[1])
    delayTime = 0.0
    
    ledStrip = LedStrip_WS2801(nrOfleds)
    
    rainbow(ledStrip, nrOfleds)

