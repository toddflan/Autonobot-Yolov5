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


def gate(a):
    y_val = []
    for i in range(len(a)):
        y_val.append(a[i].yMin)

    y_val.sort(reverse=True)

    x_left = 0
    x_right = 0
    for i in range(len(a)):
        if a[i].yMin == y_val[0]:
            x_left = a[i].xMax
        if a[i].yMin == y_val[1]:
            x_right = a[i].xMin

    if x_left > x_right:
        temp = x_left
        x_left = x_right
        x_right = temp
    return x_left, x_right


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
        # print("Width =", GetSystemMetrics(0))
        dimension = pyautogui.size()
        x_rover = dimension[0] / 2
        # print("Height =", GetSystemMetrics(1))
        
        print('# of AMs:', len(rover.arucoMarkers), '; # of cones', len(rover.cones))
        
        for arucoMarker in rover.arucoMarkers:
            print(arucoMarker)
        for cone in rover.cones:
            print(cone)
        if len(rover.arucoMarkers) == 0 and len(rover.cones) == 2:
            rover.PressGas()
            rover.GoStraight().For(1.5)
        # elif len(rover.arucoMarkers) == 1:
        #     if x_rover < rover.arucoMarkers[0].xMin:
        #         rover.PressGas()
        #         rover.TurnLeft().For(.05)
        #         rover.GoStraight().For(1)
        #         rover.ReleaseGas()
        else:
            ams = rover.arucoMarkers
            if len(ams) > 2:
                left, right = gate(ams)
            if len(ams) == 0:
                rover.PressGas()
                rover.TurnLeft().For(1)
                rover.GoStraight().For(.3)
                rover.ReleaseGas()

            else:
                left = 0
                right = 0
                if ams[0].xMax < ams[1].xMax:
                    left = ams[0].xMax
                    right = ams[1].xMin
                else:
                    left = ams[1].xMax
                    right = ams[0].xMin

            if left < x_rover < right:
                rover.PressGas()
                rover.GoStraight().For(1.25)
                rover.ReleaseGas()
            elif right < x_rover:
                rover.PressGas()
                rover.TurnLeft().For(.23)
                rover.GoStraight().For(.3)
                rover.ReleaseGas()
            else:
                rover.PressGas()
                rover.TurnRight().For(.2)
                rover.ReleaseGas()
        # if cone[0].xMin < x_rover < cone[1].xMin and cone[0].yMax < 790 and cone[1].yMax < 790:
        #     print("straightstraightstraightstraightstraightstraightstraightstraightstraightstraight")
        #     rover.PressGas()
        #     rover.GoStraight()
        #     rover.DriveFor(1)
        #     rover.ReleaseGas()
        # if len(cone) == 1 and cone[0].xMin < x_rover:
        #     # print("curve")
        #     # rover.TurnLeft().For(.1)
        #     # rover.GoStraight().For(.3)
        #     # rover.ReleaseGas()
        #     print("turn leftturn leftturn leftturn leftturn leftturn leftturn left")
        #     rover.TurnLeft().For(.1)
        #     rover.PressGas()
        #     rover.DriveFor(.3)
        # # if len(cone) == 2 and cone[1].xMin < x_rover:
        # if cone[1].xMin < x_rover:
        #     # print("curve")
        #     # rover.TurnLeft().For(.1)
        #     # rover.GoStraight().For(.3)
        #     # rover.ReleaseGas()
        #     print("turn leftturn leftturn leftturn leftturn leftturn leftturn left")
        #     rover.TurnLeft().For(.1)
        #     rover.PressGas()
        #     rover.DriveFor(.3)
        
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