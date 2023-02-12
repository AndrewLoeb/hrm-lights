import math
import numpy as np
import requests
import time

class nanoleafHR():
    
    def __init__(self):
        self.nPanels = 18
        self.panelIDs = [50755, 54819, 49995, 61705, 58720, 62720, 36241, 7504, 15758, 44367,
            53071, 24462, 58409, 29928, 35452, 6845, 56975, 20046]

    def animate_pulse(self, BPM):

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
        pulseSpeed = (self.nPanels + tailLen)/nFrames

        # Determine pulse position per frame
        pulsePos = []
        for f in range(int(nFrames)):
            pulsePos.append(f * pulseSpeed)

        # Determine the pulse spike and tail curve
        fp = [0] + (list(np.linspace(0, 1, tailLen))) + [0]

        # Set pulse curve per frame. List of intensity per panel, indexed by frame
        frameData = np.zeros([nFrames, self.nPanels])
        for f in range(int(nFrames)):
            xp = np.linspace(pulsePos[f]-tailLen, pulsePos[f], tailLen+2)
            frameData[f] = np.interp(range(self.nPanels), xp, fp)

        # Interpolate colors
        BPMScale = np.interp(BPM, [BPM1, BPM2], [0, 1])
        rBase = np.interp(BPMScale, [0, 1], [R1, R2])
        gBase = np.interp(BPMScale, [0, 1], [G1, G2])
        bBase = np.interp(BPMScale, [0, 1], [B1, B2])

        # Create data string
        animData = str(self.nPanels)
        for p in range(self.nPanels):
            animData += " " +str(self.panelIDs[p]) + " " + str(int(nFrames))
            for f in range(int(nFrames)):
                R = frameData[f][p] * rBase
                G = frameData[f][p] * gBase
                B = frameData[f][p] * bBase
                animData += " " + str(int(R))
                animData += " " + str(int(G))
                animData += " " + str(int(B)) + " 0 " + str(transitionTime)
        
        return animData

    def send_effeft(self, animData):
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

    def set_default():
        return None

       

