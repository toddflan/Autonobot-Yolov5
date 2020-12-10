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
        print('Analyzing screen')

        # capture the screen

        # ca1pture the screen
        now1 = time.time()

        rover.CaptureScreen()
        
        # then translate the screenshot into the form the Yolo predictor needs
        imageBGR = rover.InterpretImageAsBGR()
        
        done = time.time()
        print("time1: " + str(done - now1))

        
        # send the images through the deep learning models
        # you do not have to keep the simple structure here
        # feel free to change things however you want
        
        # getting yolo prediction, storing results in rover class variables
        rover.cones, rover.arucoMarkers = rover.Detect(imageBGR)
        
        xcenter = rover.screen.size[0]/2
        print('xcenter:',xcenter)
        ycenter = rover.screen.size[1]/2
        print('ycenter:', ycenter)
        
        cones =[]
        AMs = []
        
        print ('Number of Aruco Markers:', len(rover.arucoMarkers))
        print('Number of cones:', len(rover.cones))
        
        for arucoMarker in rover.arucoMarkers:
            print(arucoMarker)
        for cones in rover.cones:
            print(cones)
       
        if len(rover.arucoMarkers) ==0:
            print('Searching for aruco markers')
            rover.PressGas()
            rover.GoStraight().For(0.1)
            rover.TurnLeft().For(0.1)
            rover.ReleaseGas()
            
        
        elif len(rover.arucoMarkers) == 1:
            print('Only one marker detected')
            rover.PressGas()
            rover.GoStraight().For(0.1)
            rover.TurnLeft().For(0.1)
            rover.GoStraight().For(0.1)
            rover.ReleaseGas()
        
        elif len(rover.arucoMarkers) == 2:
            gate = (rover.arucoMarkers[0].xMax + rover.arucoMarkers[1].xMin)/2
            if gate < 1000:
                print("Turning left")
                rover.PressGas()
                rover.TurnLeft().For(0.1)
                rover.ReleaseGas()
            elif gate > 1200:
                print("Turning Right")
                rover.PressGas()
                rover.TurnRight().For(0.1)
                rover.ReleaseGas()
            else:
                print("Driving Forward")
                rover.PressGas()
                rover.GoStraight().For(1)

            
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
        t3 = time.time()
        print('# of AMs:', len(rover.arucoMarkers), '; # of cones', len(rover.cones))
        
        for arucoMarker in rover.arucoMarkers:
            print(arucoMarker)
        for cone in rover.cones:
            print(cone)
        
        
        print() # newline to space things out
        
        rover.PressGas()
        rover.GoStraight().For(0.1)
        #rover.ReleaseGas()

        print("TIME3",str(time.time()-t3))
        
        print("TOTAL TIME")
        print(time.time()-now1)
        print("")
    def DriveStartUp(rover):
        pass
        
    def Drive(rover):
        # use rover.cones and rover.arucoMarkers to make driving decisions
        # and go through cones
        pass
    def Run(self):
##        print(3)
##        time.sleep(0.5)
##        print(2)
##        time.sleep(0.5)
##        print(1)
##        time.sleep(0.5)
        
        self.analyzeThread = threading.Thread(target=self.AnalyzeScript)
        self.analyzeThread.start()
        
        self.drivingThread = threading.Thread(target=self.DriveScript)
        self.drivingThread.start()
        
        self.inputThread = threading.Thread(target=self.Input)
        #self.inputThread.start()
        
        self.analyzeThread.join()
        self.drivingThread.join()
        #self.inputThread.join()
                
def RunRover():
    rover = MyRover()
    
    # Initialize yolov5, can add device here to use CUDA

    #rover.InitializeYolov5("unityGameYolov5-best.pt", device='')

    rover.InitializeYolov5("unityGameYolov5-best.pt", device='1')

    
    rover.Run()

if __name__ == "__main__":
    RunRover()
