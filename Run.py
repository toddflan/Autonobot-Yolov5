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
        numCones = len(rover.cones)
                 
        if (numCones > 1):
            if ((rover.cones[0].xMin < rover.cones[1].xMin)):
                rover.cones[0].name = "L"
                rover.cones[1].name = "R"
            else:
                rover.cones[0].name = "R"
                rover.cones[1].name = "L"
            
        print('# of AMs:', len(rover.arucoMarkers), '; # of cones', len(rover.cones))
        
        print()
        
        print(rover.cones)
        
        for arucoMarker in rover.arucoMarkers:
            print(arucoMarker)
        for cone in rover.cones:
            print(cone)
        
        print() # newline to space things out
        rover.PressGas()
        rover.GoStraight().For(2)
        rover.ReleaseGas()
        
        if rover.PredictCurveStraight == "straight":
            if (numCones == 1):
                rover.PressGas()
                rover.TurnLeft().For(0.2)
                rover.GoStraight().For(1)
                rover.ReleaseGas()
            else:
                rover.PressGas()
                rover.GoStraight().For(6)
                rover.ReleaseGas()
        else:
            if ((numCones == 0) or (numCones == 1)):
                rover.PressGas()
                #rover.TurnLeft().For(0.5)
                rover.GoStraight().For(2)                
                rover.ReleaseGas()

            #else:
                #if ((rover.cones[1].xMin < (center-200))and(rover.cones[0].xMin < (center-200))):
            elif ((rover.cones[1].xMin > (center+500))and(rover.cones[0].xMin > (center+500))):
                rover.PressGas()
                rover.TurnRight().For(0.1)
                rover.GoStraight().For(0.5)
                rover.ReleaseGas()
            else:
                rover.PressGas()
                rover.TurnLeft().For(0.2)
                rover.GoStraight().For(0.5)
                rover.ReleaseGas()
                    #rover.PressGas()
                    #rover.GoStraight().For(3)
                    #rover.ReleaseGas()
        
#        if ((x - cone[0].xMax) < 0 ):
#            rover.TurnLeft().For(0.5)
#        if ((x - cone[1].xMax) > 0 ):
#            rover.TurnRight().For(0.5)
        
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