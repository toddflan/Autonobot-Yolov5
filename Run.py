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
        # print("Width =", GetSystemMetrics(0))
        dim = pyautogui.size()
        x = dim[0] / 2
        # print("Height =", GetSystemMetrics(1))

        print('# of AMs:', len(rover.arucoMarkers), '; # of cones', len(rover.cones))

        for arucoMarker in rover.arucoMarkers:
            print(arucoMarker)
        for cone in rover.cones:
            print(cone)
        # beginning of the track
        ruco = rover.arucoMarkers
        # if there are none turn left
            # if one marker go towards the marker
        if len(rover.arucoMarkers) == 0 and len(rover.cones) == 2:
            rover.PressGas()
            rover.GoStraight().For(6)
        if len(ruco) == 0:
            rover.PressGas()
            rover.TurnLeft().For(0.25)
            rover.GoStraight()
            rover.ReleaseGas()
        if len(ruco) == 1:
            if ruco[0].xMax < x:
                rover.PressGas()
                rover.TurnLeft().For(.25)
                rover.GoStraight().For(0.5)
                rover.ReleaseGas()
            if ruco[0].xMin > x:
                rover.PressGas()
                rover.TurnRight().For(.15)
                rover.GoStraight().For(0.5)
                rover.ReleaseGas()
        if len(ruco) == 2:
            left = 0
            right = 0
            if ruco[0].xMax < x < ruco[1].xMin:
                rover.PressGas()
                rover.GoStraight().For(0.5)
                rover.ReleaseGas()
            if ruco[0].xMax > x:
                rover.PressGas()
                rover.TurnRight().For(.15)
                rover.GoStraight().For(0.5)
                rover.ReleaseGas()
            else:
                rover.PressGas()
                rover.TurnLeft().For(.25)
                rover.GoStraight().For(0.5)
                rover.ReleaseGas()
        if len(ruco) > 2:
            y_min = 100000000
            for a in ruco:
                if a.yMin < y_min:
                    y_min = a.yMin

            two_cones = []
            for a in ruco:
                if abs(a.yMin - y_min) < (a.yMin * .1):
                    two_cones.append(a)
            print("TWO CONES:", len(two_cones))
            for cone in two_cones:
                print("Y MIN :", cone.yMin)
            if two_cones[0].xMin > two_cones[1].xMin:
                temp_cone = two_cones[0];
                two_cones[0] = two_cones[1]
                two_cones[1] = temp_cone

            if two_cones[0].xMax < x < two_cones[1].xMin:
                rover.PressGas()
                rover.GoStraight().For(.5)
                rover.ReleaseGas()
            elif two_cones[0].xMax > x:
                rover.PressGas()
                rover.TurnRight().For(.15)
                rover.GoStraight()
                rover.ReleaseGas()
            elif two_cones[1].xMin < x:
                rover.PressGas()
                rover.TurnLeft().For(.25)
                rover.GoStraight()
                rover.ReleaseGas()
            else:
                rover.PressGas()
                rover.GoStraight().For(0.5)
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
