import DriveAPI
import threading
import time
from math import*

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
		print('test1')
		rover.PutInDrive()
		rover.center = 950

		rover.rturn = False
		rover.lturn = False
		print('test2')
		# #Runs once when the rover is started, then Analyze is called in a loop
		# #Here is where to do any setup items, such as putting the rover in drive and pressing the gas
		
		#rover.PressGas()
		print('test3')
			
	def Analyze(rover):	
		
		print('Analysis')
		# capture the screen
		rover.CaptureScreen()

		# then translate the screenshot into the forms the CurveStraight and Yolo predictors need
		imageBGR = rover.InterpretImageAsBGR()

		# send the images through the deep learning models
		# you do not have to keep the simple structure here
		# feel free to change things however you want
		rover.cones, rover.arucoMarkers = rover.Detect(imageBGR)

		print('# of AMs:', len(rover.arucoMarkers), '; # of cones', len(rover.cones))
		for arucoMarker in rover.arucoMarkers:
            		print(arucoMarker)
		for cone in rover.cones:
			print(cone)


		print('drive')
		if((len(rover.cones) >= 2) and (rover.cones[0].yMax < 790) and (rover.cones[1].yMax < 790)):
			if ((rover.cones[0].xMax <= rover.center) and (rover.cones[1].xMin >= rover.center)):
				rover.time = (800 / (((rover.cones[0].yMax + rover.cones[1].yMax) / 2) - 300)) - 1.5
				if(rover.time < 1):
					print("straight")
					rover.GoStraight()
					rover.PressGas()
					rover.DriveFor(1)
					rover.ReleaseGas()
					rover.rturn = False
					rover.lturn = False
				else:
					print("Cone straight")
					rover.GoStraight()
					rover.PressGas()
					rover.DriveFor(rover.time)
					rover.ReleaseGas()
					rover.rturn = False
					rover.lturn = False
			elif(rover.cones[0].xMax > rover.center):
				print("turn right")
				rover.PressGas()		
				rover.TurnRight()
				if(rover.lturn):
					rover.DriveFor(0.05)
				else:
					rover.DriveFor(0.12)
				rover.GoStraight()
				rover.ReleaseGas()
				rover.rturn = True
				rover.lturn = False
			elif(rover.cones[1].xMin < rover.center):
				print("turn left")
				rover.PressGas()		
				rover.TurnLeft()
				if(rover.rturn):
					rover.DriveFor(0.05)
				else:
					rover.DriveFor(0.12)
				rover.GoStraight()
				rover.ReleaseGas()
				rover.lturn = True
				rover.rturn = False
			else:
				print('Reverse')
				rover.PutInReverse()
				rover.PressGas()
				rover.DriveFor(1)
				rover.ReleaseGas()
				rover.PutInDrive()
				rover.rturn = False
				rover.lturn = False
		
		# rover.curveStraightPrediction is string that is either "straight" or "curve"
		
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
		
		#for arucoMarker in rover.arucoMarkers:
			#print(arucoMarker)
		#for cone in rover.cones:
			#print(cone)

				
	def DriveStartUp(rover):
		pass

	def Drive(rover):
		# access rover.curveStraightPrediction, rover.curveStraightPrediction, and rover.curveStraightPrediction
		# here to make driving decisions
		pass

		
	
				
def RunRover():
    rover = MyRover()
    
    # Initialize yolov5, can add device here to use CUDA
    rover.InitializeYolov5("unityGameYolov5-best.pt", device='')
    
    rover.Run()

if __name__ == "__main__":
    RunRover()
