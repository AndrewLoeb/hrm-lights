import math
import numpy as np
import requests
import time


BPM = 80
nPanels = 18
panelIDs = [50755, 54819, 49995, 61705, 58720, 62720, 36241, 7504, 15758, 44367,
            53071, 24462, 58409, 29928, 35452, 6845, 56975, 20046]

global t1
t1 = time.time()

def animate_pulse(nPanels, panelIDs, BPM):

    pulseTime = 60/BPM
    tailLen = 18
    transitionTime = .1

    BPM1 = 50
    BPM2 = 120
    R1 = 0
    R2 = 255
    G1 = 50
    G2 = 0
    B1 = 200
    B2 = 0


    nFrames = math.ceil(pulseTime/transitionTime)
    # Panels per frame. Need to start at the head and end with the tail extinguished
    pulseSpeed = (nPanels + tailLen)/nFrames

    # Determine pulse position per frame
    pulsePos = []
    for f in range(int(nFrames)):
        pulsePos.append(f * pulseSpeed)

    # Determine the pulse spike and tail curve
    fp = [0] + (list(np.linspace(0, 1, tailLen))) + [0]

    # Set pulse curve per frame. List of intensity per panel, indexed by frame
    frameData = np.zeros([nFrames, nPanels])
    for f in range(int(nFrames)):
        xp = np.linspace(pulsePos[f]-tailLen, pulsePos[f], tailLen+2)
        frameData[f] = np.interp(range(nPanels), xp, fp)

    # Interpolate colors
    BPMScale = np.interp(BPM, [BPM1, BPM2], [0, 1])
    rBase = np.interp(BPMScale, [0, 1], [R1, R2])
    gBase = np.interp(BPMScale, [0, 1], [G1, G2])
    bBase = np.interp(BPMScale, [0, 1], [B1, B2])

    # Create data string
    animData = str(nPanels)
    for p in range(nPanels):
        animData += " " +str(panelIDs[p]) + " " + str(int(nFrames))
        for f in range(int(nFrames)):
            R = frameData[f][p] * rBase
            G = frameData[f][p] * gBase
            B = frameData[f][p] * bBase
            animData += " " + str(int(R))
            animData += " " + str(int(G))
            animData += " " + str(int(B)) + " 0 " + str(transitionTime)
    
    return animData

def send_effeft(animData):
    ipAddress = '192.168.1.160:16021'
    auth_token = 'wmo0FEovAEKpibMaVNlBjeL29AxpycJh'
    url = f'http://{ipAddress}/api/v1/{auth_token}/effects'
    myobj = {"write":{
      "command": "display",
        "version": "2.0",
      "animType": "custom",
      "palette": [],
      "colorType": "HSB",
      "loop": False,
      "animData": animData}}
    h = {"Authorization": "Bearer wmo0FEovAEKpibMaVNlBjeL29AxpycJh"}

    x = requests.put(url, headers = h, json=myobj)
    
    return x

# GPIO stuff
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

def button_callback(channel):
    global t1
    t2 = time.time()
    if (t2-t1)<0.2:
        print('bounce...')
        return
    BPM = 60/max(min(t2-t1, 3),0.5)
    t1 = t2
    animData = animate_pulse(nPanels, panelIDs, BPM)
    x = send_effeft(animData)
    
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge
message = input("Press enter to quit\n\n") # Run until someone presses enter
GPIO.cleanup() # Clean up

       
