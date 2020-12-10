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

class MyRover(DriveAPI.Rover):  
    def AnalyzeStartUp(rover):
        # Runs once when the rover is started, then Analyze is called in a loop
        # Here is where to do any setup items, such as putting the rover in drive and pressing the gas
        rover.PutInDrive()
        # rover.PressGas()
            
    def Analyze(rover):
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
        
        center = 1050
            
        print('# of AMs:', len(rover.arucoMarkers), '; # of cones', len(rover.cones))
        
        numCones = 0
        #Left/Right Labels not working

        if (len(rover.arucoMarkers) > 1):
            numCones = len(rover.arucoMarkers)
            mins = numpy.zeros(numCones)
            for i in range (numCones):
                numpy.append(mins, rover.arucoMarkers[i].yMin)

            i = numpy.argmin(mins)
            mins[i] = 100000
            j = numpy.argmin(mins)
            rover.arucoMarkers[i].name = "L"
            rover.arucoMarkers[j].name = "R"
            rightmin = rover.arucoMarkers[j].xMin
            leftmax = rover.arucoMarkers[i].xMax
            gate_center = leftmax + ((rightmin - leftmax)/2)

        elif (len(rover.arucoMarkers) == 1):
            coneMin = rover.arucoMarkers[0].xMin
            coneMax = rover.arucoMarkers[0].xMax


        else:
            numCones = len(rover.cones)
            if (numCones > 1):
                mins = numpy.zeros(numCones)
                for i in range (numCones):
                    numpy.append(mins, rover.cones[i].yMin)

                i = numpy.argmin(mins)
                mins[i] = 100000
                j = numpy.argmin(mins)
                
                rover.cones[i].name = "L"
                rover.cones[j].name = "R"
                rightmin = rover.cones[j].xMin
                leftmax = rover.cones[i].xMax
                gate_center = leftmax + ((rightmin - leftmax)/2)
            elif (numCones==1):
                coneMin = rover.cones[0].xMin
                coneMax = rover.cones[0].xMax
            else:
                numCones = 0

        print()
        
        for arucoMarker in rover.arucoMarkers:
            print(arucoMarker)
        for cone in rover.cones:
            print(cone)

        print() # newline to space things out


        if rover.PredictCurveStraight == "straight":

            rover.PressGas()
            rover.GoStraight().For(4)
            rover.ReleaseGas()

        elif (numCones > 1):
            if (center < (gate_center - 175)):
                rover.PressGas()
                rover.TurnRight().For(0.05)
                rover.GoStraight().For(0.05)
                rover.ReleaseGas()
            elif (center > (gate_center + 175)):
                rover.PressGas()
                rover.TurnLeft().For(0.1)
                rover.GoStraight().For(0.05)
                rover.ReleaseGas()
            else:
                rover.PressGas()
                rover.GoStraight().For(1)
                rover.ReleaseGas()
        elif(numCones == 1):
            if(center < coneMin):
                rover.PressGas()
                rover.TurnRight().For(0.15)
                rover.GoStraight()
                rover.ReleaseGas()
            elif(center > coneMax):
                    rover.PressGas()
                    rover.TurnLeft().For(0.15)
                    rover.GoStraight()
                    rover.ReleaseGas()
        else:
            rover.PressGas()
            #Increased turn left by 0.3
            rover.TurnLeft().For(1)
            #removed For
            rover.GoStraight()
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
    rover.InitializeYolov5("unityGameYolov5-best.pt", device='')
    
    rover.Run()

if __name__ == "__main__":
    RunRover()