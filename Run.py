import DriveAPI
import threading
import time
import pyautogui
import matplotlib.pyplot as plt
import PIL

import os

from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json
import numpy

# screen dimensions *** change screen to 1600 x 900 ***
screenDim = pyautogui.size()
minTurn = 0.01
maxTurn = 1
minForward = 1
maxForward = 5

# some function for me
def getYMax(object):
    # this will allow us to sort by closest to rover
    return object.yMax

def getGate(list):
    # function to return the points for the closest gate
    size = len(list)
    if size == 0:
        return 'none', 0, 0, 0
    else:
        list.sort(reverse=True, key=getYMax)
        
        for i in range(size-1): # get closest gate
            sameType = (list[i].name == list[i+1].name) # determine if they're part of the same gate
            closeInY = (list[i].yMax < 1.1*list[i+1].yMax) and (list[i].yMax > 0.9*list[i+1].yMax)
            if sameType and closeInY: # made a gate
                if list[i].xMin < list[i+1].xMin: # getting L and R
                    return list[i].name, list[i].xMax, list[i+1].xMin, list[i].yMax
                else:
                    return list[i].name, list[i+1].xMax, list[i].xMin, list[i].yMax
        
        # didn't find a gate
        for i in range(size):
            if list[i].yMax < 0.8*screenDim[1]: # not way at the bottom of screen
                return 'one', list[i].xMin, list[i].xMax, list[i].yMax
        
        return 'none', 0, 0, 0
        # am1 gate - AM1, am2 gate - AM2, no gate - none, single cone - one
        # gate type, left point, right point, y value

class MyRover(DriveAPI.Rover):  
    def AnalyzeStartUp(rover):
        # Runs once when the rover is started, then Analyze is called in a loop
        # Here is where to do any setup items, such as putting the rover in drive and pressing the gas
        rover.PutInDrive()
        rover.PressGas()
        rover.GoStraight().For(2)
        rover.ReleaseGas()
            
    def Analyze(rover):
        # time.sleep(1)
        
        # capture the screen
        rover.CaptureScreen()
        
        # then translate the screenshot into the form the Yolo predictor needs
        imageBGR = rover.InterpretImageAsBGR()
        
        # send the images through the deep learning models
        # you do not have to keep the simple structure here
        # feel free to change things however you want
        
        # getting yolo prediction, storing results in rover class variables
        rover.cones, rover.arucoMarkers = rover.Detect(imageBGR)
        
        # maybe process your prediction results here, or in Drive()
        
        # rover.cones is a list of objects of type Cone and has the follow members
        # name
        # xMin
        # xMax
        # yMin
        # xMax
        
        # rover.arucoMarkers is a list of objects of type ArucoMarker and has the follow members
        # name
        # xMin
        # xMax
        # yMin
        # xMax
        
        # print('# of AMs:', len(rover.arucoMarkers), '; # of cones', len(rover.cones))
        
        gate = getGate(rover.arucoMarkers)
        print(gate)
        
        # print(gate[0], gate[1], gate[2], gate[3])
        
        # for arucoMarker in sortedList:
            # print(arucoMarker)
        # for cone in rover.cones:
            # print(cone)
        
        # print() # newline to space things out
        
        # rover.PressGas()
        # rover.GoStraight().For(0.1)
        # rover.ReleaseGas()
        
        # get info from gate
        gateType = gate[0]
        leftEnd = gate[1]
        rightEnd = gate[2]
        yVal = gate[3]
        gap = rightEnd - leftEnd
        
        if gateType == 'none':
            print('cone search')
            rover.PressGas()
            rover.TurnLeft().For(maxTurn)
            rover.GoStraight()
            rover.ReleaseGas()
        # elif gateType == 'AM2': # go to outside of the gate
            # pass
        else:
            if leftEnd + gap*0.05 > screenDim[0]/2: # checking if center is between two cones
                print('turn right')
                diffNormalized = (leftEnd + gap*0.05 - screenDim[0]/2) / screenDim[0]/2
                duration = (1 - diffNormalized)*minTurn + diffNormalized*maxTurn
                print(duration)
                rover.PressGas()
                rover.TurnRight().For(duration)
                rover.GoStraight()
                rover.ReleaseGas()
            elif rightEnd - gap*0.05 < screenDim[0]/2:
                print('turn left')
                diffNormalized = (-rightEnd + gap*0.05 + screenDim[0]/2) / screenDim[0]/2
                duration = (1 - diffNormalized)*minTurn + diffNormalized*maxTurn
                print(duration)
                rover.PressGas()
                rover.TurnLeft().For(duration)
                rover.GoStraight()
                rover.ReleaseGas()
            else:
                print('straight')
                # set up a variable straight duration
                diffNormalized = (screenDim[1] - yVal) / screenDim[1]/2
                duration = (1 - diffNormalized)*minForward + diffNormalized*maxForward
                print(duration)
                rover.PressGas()
                rover.GoStraight().For(duration)
                rover.ReleaseGas()
        
    def DriveStartUp(rover):
        pass
        
    def Drive(rover):
        # use rover.cones and rover.arucoMarkers to make driving decisions
        # and go through cones
        pass
    
def RunRover():
    rover = MyRover()
    
    # Initialize yolov5, can add device here to use CUDA
    rover.InitializeYolov5("unityGameYolov5-best.pt", device='0') # 0 for CUDA gpu
    
    rover.Run()

if __name__ == "__main__":
    RunRover()
