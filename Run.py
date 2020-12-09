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


        print('# of AMs:', len(rover.arucoMarkers), '; # of cones', len(rover.cones))

        center_x = rover.screen.size[0] / 2
        center_y = rover.screen.size[1] / 2

        cones = []
        ac1 = []
        ac2 = []

        for arucoMarker in rover.arucoMarkers:
            print(arucoMarker)
            if(arucoMarker.name == "AM1"):
                area = ((arucoMarker.xMax - arucoMarker.xMin) * (arucoMarker.yMax - arucoMarker.yMin))
                ac1.append([(arucoMarker.xMin + arucoMarker.xMax) / 2 , (arucoMarker.yMin + arucoMarker.yMax) / 2, area])
            if(arucoMarker.name == "AM2"):
                area = ((arucoMarker.xMax - arucoMarker.xMin) * (arucoMarker.yMax - arucoMarker.yMin))
                ac2.append([(arucoMarker.xMin + arucoMarker.xMax) / 2 , (arucoMarker.yMin + arucoMarker.yMax) / 2, area])

        for cone in rover.cones:
            print(cone)
            area = (cone.xMax - cone.xMin) * (cone.yMax - cone.yMin)
            cones.append([(cone.xMin + cone.xMax) / 2 , (cone.yMin + cone.yMax) / 2 , area])

        cones = sorted(cones, key=lambda x: x[2], reverse=True)

        print(cones)
        # if(len(cones) > 1):
        #     if(cones[0][0] > 0.9 * center_x and cones[0][0] < 1.1 * center_x and cones[0][1] < center_y):
        #         print("reversing")
        #         rover.PressGas()
        #         rover.PutInReverse()
        #         rover.GoStraight().For(1)
        #         rover.PutInDrive()
        #         rover.ReleaseGas()
        #         return

        TA = 0.01
        SA = 4.5

        in_marker = ac1
        out_marker = ac2

        domimant = "in"

        margL = 0.95
        margR = 1.05

        if len(ac1) == 0 and len(ac2) == 0:
            if len(cones) == 1:
                if cones[0][0] < center_x:
                    print("no marker, turn left")
                    rover.PressGas()
                    rover.TurnLeft().For(0.1)
                    rover.GoStraight()
                    rover.ReleaseGas()
                if cones[0][0] >= center_x and cones[0][1] >= center_y:
                    print("no marker, turn right")
                    rover.PressGas()
                    rover.TurnRight().For(0.1)
                    rover.GoStraight()
                    rover.ReleaseGas()
            if len(cones) >= 2:
                print(center_x, cones[0][0], cones[1][0])
                if cones[0][0] <= center_x and cones[1][0] >= center_x or cones[1][0] <= center_x and cones[0][0] >= center_x:
                    print("no maker, go straight")
                    rover.PressGas()
                    rover.GoStraight().For(SA)
                    rover.ReleaseGas()
                else:
                    print("Idk what to do?")
                    rover.PressGas()
                    rover.GoStraight().For(TA)
                    rover.ReleaseGas()


        if(len(in_marker) > 0 and len(out_marker) > 0):
            if(in_marker[0][2] < out_marker[0][2]):
                domimant = "out"
        elif len(in_marker) == 0 and len(out_marker) > 0:
            domimant = "out"


        if domimant == "in":
            if len(in_marker) == 1:
                if in_marker[0][0] <= center_x * 0.5:
                    print("one through aruco, turn big left")
                    rover.PressGas()
                    rover.TurnLeft().For(0.4)
                    rover.GoStraight()
                    rover.ReleaseGas()
                if in_marker[0][0] < center_x:
                    print("one through aruco, turn left")
                    rover.TurnLeft().For(TA)
                    rover.PressGas().For(0.01)
                    rover.GoStraight().For(0.01)
                    rover.ReleaseGas().For(0.01)
                    rover.GoStraight()
                elif in_marker[0][0] >= center_x: #and cones[0][1] >= center_y:
                    print("one through aruco, turn right")
                    rover.TurnRight().For(TA)
                    rover.PressGas().For(0.01)
                    rover.GoStraight().For(0.01)
                    rover.ReleaseGas().For(0.01)
                    rover.GoStraight()
            elif len(in_marker) >= 2:
                if in_marker[0][0] <= margL * center_x and in_marker[1][0] >= margR * center_x or in_marker[1][0] <= margL * center_x and in_marker[0][0] >= margR * center_x:
                    print("two through aruco, go straight")
                    rover.PressGas()
                    rover.GoStraight().For(SA)
                    rover.ReleaseGas()
                elif in_marker[0][0] <= center_x * 0.6 and in_marker[1][0] <= center_x * 0.6:
                    print("two through aruco, turn big left")
                    #rover.PressGas()
                    rover.PressGas()
                    rover.TurnLeft().For(0.4)
                    rover.GoStraight()
                    rover.ReleaseGas()
                elif in_marker[0][0] <= margR * center_x and in_marker[1][0] <= margR * center_x:
                    print("two through aruco, turn left")
                    #rover.PressGas()
                    rover.TurnLeft().For(TA)
                    rover.PressGas().For(0.01)
                    rover.GoStraight().For(0.01)
                    rover.ReleaseGas().For(0.01)
                    rover.GoStraight()
                elif in_marker[0][0] >= margL * center_x  and in_marker[1][0] >= margL * center_x:
                    print("two through aruco, turn right")
                    rover.TurnRight().For(TA)
                    rover.PressGas().For(0.01)
                    rover.GoStraight().For(0.01)
                    rover.ReleaseGas().For(0.01)
                    rover.GoStraight()
                else:
                    print("two pass aruco, nudge forward")
                    rover.PressGas()
                    rover.GoStraight().For(SA / 4)
                    rover.ReleaseGas()

        elif domimant == "out":
            if len(out_marker) == 1:
                if out_marker[0][0] < center_x / 2 and out_marker[0][1] > center_y:
                    print("set alignment, pass aruco, turn left")
                    rover.TurnLeft().For(TA)
                    rover.PressGas().For(0.01)
                    rover.GoStraight().For(0.01)
                    rover.ReleaseGas().For(0.01)
                    rover.GoStraight()
                    rover.GoStraight().For(SA / 4)
                    rover.ReleaseGas()
                elif out_marker[0][0] > center_x + center_x / 4 and out_marker[0][1] > center_y - (center_y / 4):
                    print("set alignment, pass aruco, turn right")
                    rover.TurnRight().For(TA)
                    rover.PressGas().For(0.01)
                    rover.GoStraight().For(0.01)
                    rover.ReleaseGas().For(0.01)
                    rover.GoStraight()
                    rover.GoStraight().For(SA / 4)
                    rover.ReleaseGas()
                elif out_marker[0][0] < center_x:
                    print("one pass aruco, turn left")
                    rover.PressGas()
                    rover.GoStraight().For(SA / 4)
                    rover.ReleaseGas()
                elif out_marker[0][0] >= center_x:
                    print("one pass aruco, turn right")
                    rover.PressGas()
                    rover.GoStraight().For(SA / 4)
                    rover.ReleaseGas()
            elif len(out_marker) >= 2:
                if out_marker[0][0] <= center_x and out_marker[1][0] >= center_x or out_marker[1][0] <= center_x and out_marker[0][0] >= center_x:
                    print("two pass aruco, go straight")
                    rover.PressGas()
                    rover.TurnRight().For(0.2)
                    rover.GoStraight().For(0.1)
                    rover.GoStraight().For(0.1)
                    rover.ReleaseGas()
                    rover.GoStraight()
                elif out_marker[0][0] <= center_x and out_marker[1][0] <= center_x:
                    print("two pass aruco, turn left")
                    rover.PressGas()
                    rover.GoStraight().For(SA / 2)
                    rover.ReleaseGas()
                elif out_marker[0][0] >= center_x  and out_marker[1][0] >= center_x:
                    print("two pass aruco, turn left")
                    rover.PressGas()
                    rover.GoStraight().For(SA / 2)
                    rover.ReleaseGas()
                else:
                    print("two pass aruco, nudge forward")
                    rover.PressGas()
                    rover.TurnLeft().For(TA)
                    rover.ReleaseGas()
                    rover.GoStraight()



        if len(out_marker) == 0 and len(in_marker) == 0 and len(cones) == 0:
                print("no cones nudge left")
                rover.PressGas()
                rover.TurnLeft().For(1)
                rover.GoStraight()
                rover.ReleaseGas()

        #time.sleep(3)
        print() # newline to space things out


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
