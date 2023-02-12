#import math
#import numpy as np
#import requests
import time

from nanoleafAPI import *
from polarBluez import *

global t1
t1 = time.time()

lines = nanoleafHR()
polarHRM = polarHRM()

polarHRM.ConnectToHR()

while True:
    try:
        polarHRM.ConnectToHR()
        BPM = polarHRM.readHR()
        print(BPM)
        if BPM==0:
            sleep(1)
            continue
        animData = lines.animate_pulse(BPM)
        lines.send_effeft(animData)
        sleep(60/BPM)
    except KeyboardInterrupt:
        print("Quitting")
        polarHRM.DisconnectToHR()


       

