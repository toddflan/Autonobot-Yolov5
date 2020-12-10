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

screen_x, screen_y = pyautogui.size()

class MyRover(DriveAPI.Rover):  
    def AnalyzeStartUp(rover):
        # Runs once when the rover is started, then Analyze is called in a loop
        # Here is where to do any setup items, such as putting the rover in drive and pressing the gas
        rover.PutInDrive()
        rover.PressGas()
        rover.GoStraight().For(1)
        rover.ReleaseGas()
            
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
        
        print() # newline to space things out

        if len(rover.cones) >= 2:
            condition = False
            if len(rover.cones) == 2:
                if 0 < abs(rover.cones[0].yMin - rover.cones[1].yMin) < 50:
                    rover.cones[0] = rover.cones[0]
                    rover.cones[1] = rover.cones[1]
            else:
                if rover.cones[0].yMax > rover.cones[1].yMax:
                    max = rover.cones[0].yMax
                    second_max = rover.cones[1].yMax
                else:
                    max = rover.cones[1].yMax
                    second_max = rover.cones[0].yMax

                for i in range(2, len(rover.cones)):
                    if rover.cones[i].yMax <= max and rover.cones[i].yMax >= second_max:
                        second_max = rover.cones[i].yMax
                    elif rover.cones[i].yMax >= max:
                        copy = max
                        max = rover.cones[i].yMax
                        second_max = copy

                for i in range(len(rover.cones)):
                    for j in range(len(rover.cones)):
                        if (rover.cones[i].yMax == max or rover.cones[i].yMax == second_max) and (rover.cones[j].yMax == max or rover.cones[j].yMax == second_max):
                            if 0 < abs(rover.cones[i].yMin - rover.cones[j].yMin) < 50 and 0 <= abs(rover.cones[i].yMax - rover.cones[j].yMax) < 50:
                                rover.cones[0] = rover.cones[i]
                                rover.cones[1] = rover.cones[j]
                                condition = True
                        if condition == True:
                            break
                    if condition == True:
                        break
        elif len(rover.cones) == 1 and len(rover.arucoMarkers) > 0:
            if rover.cones[0].xMax < 500:
                rover.PressGas()
                rover.TurnLeft().For(0.075)
                rover.GoStraight()
                rover.ReleaseGas()
            if rover.cones[0].xMax > 500:
                rover.PressGas()
                rover.TurnRight().For(0.075)
                rover.GoStraight()
                rover.ReleaseGas()
        elif len(rover.arucoMarkers) < 2 and len(rover.cones) > 0:
            rover.PressGas()
            rover.DriveFor(0.5)
            rover.ReleaseGas()
        elif len(rover.cones) == 0:
            rover.PressGas()
            rover.TurnLeft().For(1)
            rover.GoStraight()
            rover.ReleaseGas()

        marker_condition = False
        if len(rover.cones) > 0 and len(rover.arucoMarkers) >= 2:
            if len(rover.cones) >= 2:
                if rover.cones[0].xMin > rover.cones[1].xMin:
                    copy = rover.cones[0]
                    rover.cones[0] = rover.cones[1]
                    rover.cones[1] = copy

                left_barrier = [rover.cones[0].xMin - 25, rover.cones[0].xMax + 25]
                right_barrier = [rover.cones[1].xMin - 25, rover.cones[1].xMax + 25]

                if len(rover.arucoMarkers) == 2:
                    if 0 < abs(rover.arucoMarkers[0].yMin - rover.arucoMarkers[1].yMin) < 50:
                        rover.arucoMarkers[0] = rover.arucoMarkers[0]
                        rover.arucoMarkers[1] = rover.arucoMarkers[1]

                if rover.arucoMarkers[0].yMax > rover.arucoMarkers[1].yMax:
                    third_max = rover.arucoMarkers[0].yMax
                    fourth_max = rover.arucoMarkers[1].yMax
                else:
                    third_max = rover.arucoMarkers[1].yMax
                    fourth_max = rover.arucoMarkers[0].yMax

                for i in range(2, len(rover.arucoMarkers)):
                    if rover.arucoMarkers[i].yMax <= third_max and rover.arucoMarkers[i].yMax >= fourth_max:
                        fourth_max = rover.arucoMarkers[i].yMax
                    elif rover.arucoMarkers[i].yMax >= third_max:
                        marker_copy = third_max
                        third_max = rover.arucoMarkers[i].yMax
                        fourth_max = marker_copy

                first_condition = False
                second_condition = False
                for i in range(len(rover.arucoMarkers)):
                    for j in range(len(rover.cones)):
                        if first_condition == False and 0 < abs(rover.cones[j].yMin - rover.arucoMarkers[i].yMin) < 50 and 0 < abs(rover.cones[j].yMax - rover.arucoMarkers[i].yMax) < 50:
                            rover.arucoMarkers[0] = rover.arucoMarkers[i]
                            first_condition = True
                        elif second_condition == False and 0 < abs(rover.cones[j].yMin - rover.arucoMarkers[i].yMin) < 50 and 0 < abs(rover.cones[j].yMax - rover.arucoMarkers[i].yMax) < 50:
                            rover.arucoMarkers[1] = rover.arucoMarkers[i]
                            second_condition = True

                        if first_condition == True and second_condition == True:
                            break
                    if first_condition == True and second_condition == True:
                        break


                if rover.arucoMarkers[0].xMin > rover.arucoMarkers[1].xMin:
                    mark_copy = rover.arucoMarkers[0]
                    rover.arucoMarkers[0] = rover.arucoMarkers[1]
                    rover.arucoMarkers[1] = mark_copy
                if len(rover.arucoMarkers) > 0 and rover.arucoMarkers[0].name == "AM2" and rover.arucoMarkers[1].name == "AM2":
                    marker_condition = False
                    print("Pass")
                if len(rover.arucoMarkers) > 0 and rover.arucoMarkers[0].name == "AM1" and rover.arucoMarkers[1].name == "AM1":
                    marker_condition = True
                    print("Pierce")

                if marker_condition == True:
                    if left_barrier[1] < screen_x / 2 < right_barrier[0]:
                        rover.PressGas()
                        rover.DriveFor(1.75)
                        rover.ReleaseGas()
                    elif left_barrier[0] < screen_x / 2 < left_barrier[1]:
                        rover.PressGas()
                        rover.TurnRight().For(0.01)
                        rover.GoStraight()
                        rover.ReleaseGas()
                    elif right_barrier[0] < screen_x / 2 < right_barrier[1]:
                        rover.PressGas()
                        rover.TurnLeft().For(0.01)
                        rover.GoStraight()
                        rover.ReleaseGas()
                    elif rover.cones[1].xMax < screen_x / 2:
                        rover.PressGas()
                        rover.TurnLeft().For(0.05)
                        rover.GoStraight()
                        rover.ReleaseGas()
                    elif rover.cones[0].xMin > screen_x / 2:
                        rover.PressGas()
                        rover.TurnRight().For(0.05)
                        rover.GoStraight()
                        rover.ReleaseGas()
                elif marker_condition == False:
                    if rover.cones[1].xMax < screen_x / 2 or rover.cones[0].xMin > screen_x / 2:
                        rover.PressGas()
                        rover.DriveFor(1.75)
                        rover.ReleaseGas()
                    elif left_barrier[0] < screen_x / 2 < left_barrier[1]:
                        rover.PressGas()
                        rover.TurnLeft().For(0.01)
                        rover.GoStraight()
                        rover.ReleaseGas()
                    elif right_barrier[0] < screen_x / 2 < right_barrier[1]:
                        rover.PressGas()
                        rover.TurnRight().For(0.01)
                        rover.GoStraight()
                        rover.ReleaseGas()
                    elif left_barrier[1] < screen_x / 2 < right_barrier[0]:
                        rover.PressGas()
                        rover.TurnRight().For(0.05)
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
