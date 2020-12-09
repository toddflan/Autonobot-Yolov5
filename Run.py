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
        
        print('# of AMs:', len(rover.arucoMarkers), '; # of cones', len(rover.cones))
        
        for arucoMarker in rover.arucoMarkers:
            print(arucoMarker)
        for cone in rover.cones:
            print(cone)
            
        
        
        print("checking")
        
        if len(rover.arucoMarkers)>1:
            rover.target = (rover.arucoMarkers[0].xMax + rover.arucoMarkers[1].xMin)/2
            if rover.target < 1000:
                print("")
                print("going Left//////////////////////////////////////////////////////////////////////////////")
                rover.PressGas()
                rover.TurnLeft().For(.001)
                rover.ReleaseGas()
                rover.GoStraight().For(0.1)
                
            elif rover.target >1130:
                print("")
                print("going Right/////////////////////////////////////////////////////////////////////////////")
                rover.PressGas()
                rover.TurnRight().For(.001)
                rover.ReleaseGas()
                rover.GoStraight().For(0.1)
                
            else:
                print("")
                print("Straight////////////////////////////////////////////////////////////////////////////////")
                rover.PressGas()
                rover.GoStraight().For(0.1)
                rover.ReleaseGas()
        
        else:
            print("")
            print("No Markers///////////////////////////////////////////////////////////////////////////")
            rover.PressGas()
            rover.TurnLeft().For(.001)
            rover.ReleaseGas()
            rover.GoStraight().For(0.1)
            
            
        
        rover.PressGas()
        rover.GoStraight().For(0.1)
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