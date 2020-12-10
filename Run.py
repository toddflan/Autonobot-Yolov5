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
import math 

class MyRover(DriveAPI.Rover):              
    def Analyze(rover):
        #while rover.predictionTracker <= rover.predictionCount and rover.state != MyRover.forceStopped:
        #    time.sleep(.1)
            
        
            
        startTime = time.time()
        
        # capture the screen
        rover.CaptureScreen()
        imageBGR = rover.InterpretImageAsBGR()   
        rover.cones, rover.arucoMarkers = rover.Detect(imageBGR)
        
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
        # marker
        
        # for arucoMarker in rover.arucoMarkers:
            # print(arucoMarker)
                
        endTime = time.time()
        #print("\n")
        #print("Time: " + str(endTime - startTime))
        #for cone in rover.cones:
        #    print(cone)
        
        rover.closestCones = rover.SelectTwoClosestMarkers()
        #print("Closest Cones:")
        #for marker in rover.closestCones:
            #print(marker)
        
        rover.closestConesCount = 2
        if rover.closestCones[1] is None:
            rover.closestConesCount = 1
        if rover.closestCones[0] is None:
            rover.closestConesCount = 0
            
        rover.midPoint = rover.screenWidth / 2
        if rover.closestCones[0] is not None and rover.closestCones[0].name == "AM2":
            #print("HERE!!!!!!!!!!!!")
            if rover.closestConesCount == 1:
                #print("HERE!!!!!!!!!!!!")
                rover.midPoint = rover.closestCones[0].xMax + 3.5 * (rover.closestCones[0].xMax - rover.closestCones[0].xMin)
            elif rover.closestConesCount >= 2:
                rover.midPoint = max(
                    rover.closestCones[0].xMax + 3.5 * (rover.closestCones[0].xMax - rover.closestCones[0].xMin),
                    rover.closestCones[1].xMax + 3.5 * (rover.closestCones[1].xMax - rover.closestCones[1].xMin)            
                    )
        else:
            if rover.closestConesCount == 1:
                rover.midPoint = .85 * (rover.closestCones[0].xMax - rover.closestCones[0].xMin) / 2
            elif rover.closestConesCount >= 2:
                rover.midPoint = rover.closestCones[0].xMax + (rover.closestCones[1].xMin - rover.closestCones[0].xMax) / 2
        
                    
        if rover.predictionCount == 0:
            rover.PutInDrive()
            rover.PressGas()
        
        rover.predictionCount = rover.predictionCount + 1
        
        
        
        
        # os.system('cls')
        
    def Drive(rover):
        
        while rover.predictionCount == 0:
            time.sleep(.1)
            
        if rover.firstDrive:
            rover.GoStraight().For(1)
            rover.firstDrive = False
        
        # currentPredictionCount = rover.predictionCount
        # while currentPredictionCount == rover.predictionCount:
            # time.sleep(.01)
            
                
        closestCones = rover.closestCones
        closestConesCount = rover.closestConesCount
        midPoint = rover.midPoint
                    
        # if len(rover.cones) == 0: 
            # rover.noConeCounter += 1
            # if rover.noConeCounter == 2:
                # rover.noConeCounter = 0
                # rover.DriveLeft(.5)
                # print("No Cones Detected, Turn")
                
        # else:
            # midPoint = rover.cones[0].xMax + (rover.cones[1].xMin - rover.cones[0].xMax) / 2;
            
            # print("MidPoint: " + str(midPoint))
            
            # coneHeight = min(rover.cones[0].yMin, rover.cones[1].yMin)
            # print("Cone Hieght: " + str(coneHeight))
            # if coneHeight > .55 * rover.screenHeight:
                # # if rover.curveStraightPrediction == "straight":
                # print("Cones up close, drive past, on straight")
                # rover.DriveStraight(1.5)
                # # else:
                    # # print("Cones up close, drive past, on curve")
                    # # rover.DriveLeft(.4)
                    # # #rover.DriveStraight(.25)
                    # # #rover.Halt()
                    
            # else:
        bound = rover.screenWidth * .1 #was .07
        coneBound = rover.screenWidth * .05
        
        if closestConesCount >= 1 and closestCones[0].name == "AM2":
            bound = rover.screenWidth * .05 #was .07
        
        driveInterval = .05
                
        cone0AreaPercentage = 0
        cone1AreaPercentage = 0
        if closestConesCount >= 1:
            cone0AreaPercentage = rover.ConeArea(closestCones[0]) / (rover.screenWidth * rover.screenHeight)
        if closestConesCount >= 2:
            cone1AreaPercentage = rover.ConeArea(closestCones[1]) / (rover.screenWidth * rover.screenHeight)
            
        if closestConesCount >= 1 and closestCones[0].name == "AM2":
            rover.arucoMarker2Counter = rover.arucoMarker2Counter + 1
            if rover.arucoMarker2Counter >= 5:
                print("Set Bump True")
                print(rover.arucoMarker2Counter)
                rover.useBump = True
        elif closestConesCount >= 1 and closestCones[0].name == "AM1":
            rover.arucoMarker2Counter = 0
            
        # print('\n')
        # print('Aruco Markers Picked Up: ' + str(len(rover.arucoMarkers)))
        # print('Cone 0 Area Percentage: ' + str(cone0AreaPercentage))
        # print('Cone 1 Area Percentage: ' + str(cone1AreaPercentage))
        # print('Aruco Marker 1: ' + str(closestCones[0]))
        # print('Aruco Marker 2: ' + str(closestCones[1]))
        # print('Midpoint %: ' + str(round(100 * midPoint / rover.screenWidth)) + " %")
        # print('Midpoint: ' + str(midPoint))
        
        
        
        if cone0AreaPercentage == 0 and cone1AreaPercentage == 0:
            if rover.direction != rover.left:
                rover.TurnLeft()
        elif max(cone0AreaPercentage, cone1AreaPercentage) < .00055 and midPoint >= (rover.screenWidth / 2) - (bound) and midPoint <= (rover.screenWidth / 2) + (bound): #was .0007
            # print("Far away go forward")
            if rover.direction != rover.straight:
                rover.GoStraight()
        elif cone0AreaPercentage != 0 and closestCones[0].xMax >= rover.screenWidth / 2 - coneBound and closestCones[0].xMax <= rover.screenWidth / 2 + coneBound and cone0AreaPercentage > .005:
            # print("Nudge Right")
            if rover.direction != rover.right:
                rover.TurnRight()
        elif cone1AreaPercentage != 0 and closestCones[1].xMin >= rover.screenWidth / 2 - coneBound and closestCones[1].xMin <= rover.screenWidth / 2 + coneBound and cone1AreaPercentage > .005:
            # print("Nudge Left")
            if rover.direction != rover.left:
                rover.TurnLeft()
        elif max(cone0AreaPercentage, cone1AreaPercentage) >= .0019 and midPoint >= rover.screenWidth / 2 - bound and midPoint <= rover.screenWidth / 2 + bound:
            print("Blaze AHEAD!")
            # if closestCones[0].name == "AM1":
            if rover.useBump == False:
                rover.GoStraight().For(.6)
            else:
                for i in range(4):
                    print("BUMP!")
                    rover.TurnLeft()
                    rover.GoStraight()
                rover.useBump = False
                    
        elif midPoint >= (rover.screenWidth / 2) - bound and midPoint <= (rover.screenWidth / 2) + bound: # or (rover.cones[0].xMax < rover.screenWidth / 2 -  2 * bound and rover.cones[1].xMin > rover.screenWidth / 2 +  2 * bound ):
            #print("Proceed Forward!")
            if rover.direction != rover.straight:
                rover.GoStraight()
        else:            
            if midPoint <= rover.screenWidth / 2 - bound:
                #print("Proceed Left!")
                if rover.direction != rover.left:
                    rover.TurnLeft()
            else:
                #print("Proceed Right!")
                if rover.direction != rover.right:
                    rover.TurnRight()
                        
        
    def SelectTwoClosestCones(rover):
        coneAreas = []
        #for cone in rover.cones:
        #    coneAreas.append([rover.ConeArea(cone), cone])
            
        for cone in rover.cones:
            coneAreas.append([cone.yMax, rover.screenWidth - cone.xMax, cone])
        
        try:
            coneAreas.sort(reverse=True)
        except Exception as e:
            print("An exception occurred!!!!!!!!!!!!!!!")
            #print(str(e))
            #print(coneAreas)
            #rover.state = MyRover.forceStopped
            return [rover.closestCones[0], rover.closestCones[1]]
        
        result = []
        
        for i in range(min(len(coneAreas), 2)):
            result.append(coneAreas[i][2])
        
        if len(result) == 2:
            if coneAreas[1][0] < .8 * coneAreas[0][0] : 
                result[1] = None
        
        while len(result) < 2:
            result.append(None)
        
        return result
        
    def SelectTwoClosestMarkers(rover):
        coneAreas = []
        #for cone in rover.cones:
        #    coneAreas.append([rover.ConeArea(cone), cone])
            
        for marker in rover.arucoMarkers:
            #print(marker)
            coneAreas.append([marker.yMax, rover.screenWidth - marker.xMax, marker])
        
        try:
            coneAreas.sort(reverse=True)
        except Exception as e:
            print("An exception occurred!!!!!!!!!!!!!!!")
            #print(str(e))
            #print(coneAreas)
            #rover.state = MyRover.forceStopped
            return [rover.closestCones[0], rover.closestCones[1]]
        
        result = []
        
        for i in range(min(len(coneAreas), 2)):
            result.append(coneAreas[i][2])
        
        if len(result) == 2:
            if coneAreas[1][0] < .7 * coneAreas[0][0] : 
                result[1] = None
        
        while len(result) < 2:
            result.append(None)
        
        return result
        
    def AnalyzeStartUp(rover):
        rover.curveStraightPrediction = "straight"
        rover.predictionCount = 0
        rover.predictionTracker = 1
        
        # rover.screenWidth = 1600
        # rover.screenHeight = 900
        rover.screenWidth = 1920
        rover.screenHeight = 1080
        
        rover.belowCounter = 0
        rover.noConeCounter = 0
        
        rover.noDrive = False
        #rover.maxArea = .006
        #rover.maxArea = .0014
        rover.areaCalc = .016
        
        rover.lock = 0
        
        rover.cones = []
        rover.closestCones = [None, None]
        
    def DriveStartUp(rover):
        rover.firstDrive = True
        rover.arucoMarker2Counter = 0
        rover.useBump = False
        pass
        
    def DriveStraight(rover, time):
        if rover.noDrive:
            return
        #rover.PutInDrive()
        #rover.PressGas()
        rover.GoStraight().For(time)
        #rover.Halt()

    def DriveLeft(rover, time):
        if rover.noDrive:
            return
        print("Turn Left Time: " + str(time))
        #rover.PutInDrive()
        #rover.PressGas()
        rover.TurnLeft().For(time)
        #rover.Halt()

    def DriveRight(rover, time):
        if rover.noDrive:
            return
        print("Turn Right Time: " + str(time))
        #rover.PutInDrive()
        #rover.PressGas()
        rover.TurnRight().For(time)
        #rover.Halt()
        
    def Halt(rover):
        if rover.noDrive:
            return
        rover.PutInReverse()
        rover.GoStraight().For(.1)
        rover.ReleaseGas()
        
    def NudgeLeft(rover):
        if rover.noDrive:
            return
        print("Nudge Left")
        #rover.PutInDrive()
        rover.TurnLeft().For(.05)
        #rover.PressGas()
        #rover.Halt()
        
    def NudgeRight(rover):
        if rover.noDrive:
            return
        print("Nudge Right")
        #rover.PutInDrive()
        rover.TurnRight().For(.05)
        #rover.PressGas()
        #rover.Halt()
    
    def ConeArea(rover, cone):
        return (cone.xMax - cone.xMin) * (cone.yMax - cone.yMin)
        
    def StraightTime(rover, coneAreaPercentage):
        # c = 2757.756
        # b = -199.637
        # a = 3.9594
        # sleep = c * coneAreaPercentage * coneAreaPercentage + b * coneAreaPercentage + a
        # sleep = max(sleep, .25)
        
        # a = 3.444105471
        # b = -107.1880614
        
        # a = 4.055897667
        # b = -118.6206884
        # sleep = a * math.exp(b * coneAreaPercentage) * .7
        
        split = .5
        
        a = 6.978800311
        b = -265.4683707
        sleep = .62 * a * math.exp(b * coneAreaPercentage) * (((rover.areaCalc - coneAreaPercentage) / rover.areaCalc) * split + 1 - split)
        
        if rover.cones[0].xMax >= (rover.screenWidth / 2 - .1 * rover.screenWidth) or rover.cones[1].xMin <= (rover.screenWidth / 2 + .1 * rover.screenWidth):
            print("Cone in bound, reduce distance")
            sleep = sleep * .7
        
        sleep = min(sleep, 7)
        sleep = max(sleep, .5)
        print("Drive straight time: " + str(sleep))
        return sleep
        
        
def RunRover():
    rover = MyRover()
    
    # Initialize yolov5, can add device here to use CUDA
    rover.InitializeYolov5("unityGameYolov5-best.pt", device='1')
    
    rover.Run()

if __name__ == "__main__":
    RunRover()