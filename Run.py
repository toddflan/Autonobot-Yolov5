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
        rover.newYoloPrediction = False
        # Runs once when the rover is started, then Analyze is called in a loop
        # Here is where to do any setup items, such as putting the rover in drive and pressing the gas
        rover.PutInDrive()
        # rover.PressGas()
            
    def Analyze(rover):
        if not(rover.newYoloPrediction): # makes sure the screenshot is current
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
            
            for arucoMarker in rover.arucoMarkers:
                print(arucoMarker)
            for cone in rover.cones:
                print(cone)
            
            print() # newline to space things out
            
            rover.newYoloPrediction = True
        
    def DriveStartUp(rover):
        pass
        
    def Drive(rover):
        # use rover.cones and rover.arucoMarkers to make driving decisions
        # and go through cones
        if rover.newYoloPrediction:
            rover.PressGas()
            rover.GoStraight().For(0.1)
            rover.ReleaseGas()
            rover.newYoloPrediction = False
    
                
def RunRover():
    rover = MyRover()
    
    # Initialize yolov5, can add device here to use CUDA
    rover.InitializeYolov5("unityGameYolov5-best.pt", device='')
    
    rover.Run()

if __name__ == "__main__":
    RunRover()