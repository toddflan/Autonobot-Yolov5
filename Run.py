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
		rover.PutInDrive()
		
		rover.xmax = 1920
		rover.ymax = 1080
		rover.center = rover.xmax/2

		rover.rturn = False
		rover.lturn = False
		# #Runs once when the rover is started, then Analyze is called in a loop
		# #Here is where to do any setup items, such as putting the rover in drive and pressing the gas
		
		#rover.PressGas()
			
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
		for i in range(len(rover.arucoMarkers) - 1, -1, -1):
			if(rover.arucoMarkers[i].yMax > 875*(rover.ymax/1080)):
				rover.arucoMarkers.remove(rover.arucoMarkers[i])
		for i in range(len(rover.cones)):
			print(rover.cones[i])
		for i in range(len(rover.cones) - 1, -1, -1):
			if(rover.cones[i].yMax >= 1003*(rover.ymax/1080)):
				rover.cones.remove(rover.cones[i])

		print('drive')
		if(len(rover.arucoMarkers) >= 1):
			rover.am = rover.arucoMarkers[0]

			for i in range(1, len(rover.arucoMarkers)):
				if(rover.arucoMarkers[i].yMax > rover.am.yMax):
					rover.am = rover.arucoMarkers[i]
			# print(rover.am.name)
		
		
		if(len(rover.cones) >= 2):
			# Deciding left and right cones
			# potential problem if only one cone in the pair is shown 
			if(rover.cones[0].yMin > rover.cones[1].yMin):
				rover.leftcone = rover.cones[0]
				rover.rightcone = rover.cones[1]
			else:
				rover.leftcone = rover.cones[1]
				rover.rightcone = rover.cones[0]
			
			for i in range(2, len(rover.cones)):
				if(rover.cones[i].yMin > rover.leftcone.yMin):
					rover.rightcone = rover.leftcone
					rover.leftcone = rover.cones[i]
				elif(rover.cones[i].yMin > rover.rightcone.yMin):
					rover.rightcone = rover.cones[i]

			if(rover.leftcone.xMin > rover.rightcone.xMin):
				rover.conetemp = rover.leftcone
				rover.leftcone = rover.rightcone
				rover.rightcone = rover.conetemp

			if((rover.leftcone.yMax >= rover.rightcone.yMax + 250) and (len(rover.arucoMarkers) >= 1)):
				if(rover.am.name == 'AM2'):
					rover.rightcone = rover.leftcone
			# print(rover.leftcone)
			# print(rover.rightcone)

			if((len(rover.arucoMarkers) == 0) or rover.am.name == 'AM1'):
				if ((rover.leftcone.xMax <= rover.center - 30*(rover.xmax/1920)) and (rover.rightcone.xMin >= rover.center + 30*(rover.xmax/1920))):
					rover.time = pow((1080/rover.ymax)*((rover.leftcone.yMax + rover.rightcone.yMax) / 2),-6.055)*129000000000000000
					if(rover.time < 1):
						print("straight")
						rover.GoStraight()
						rover.PressGas()
						rover.DriveFor(1)
						rover.ReleaseGas()
						rover.rturn = False
						rover.lturn = False
						rover.DriveFor(1.5)
					else:
						print("Cone straight")
						rover.GoStraight()
						rover.PressGas()
						rover.DriveFor(rover.time)
						rover.ReleaseGas()
						rover.rturn = False
						rover.lturn = False
						rover.DriveFor(1.5)
				elif(rover.leftcone.xMax > rover.center - 40*(rover.xmax/1920)):
					print("turn right")
					rover.PressGas()		
					rover.TurnRight()
					rover.DriveFor(0.004)
					rover.GoStraight()
					rover.ReleaseGas()
					rover.rturn = True
					rover.lturn = False
					rover.DriveFor(1)
				elif(rover.rightcone.xMin < rover.center + 40*(rover.xmax/1920)):
					print("turn left")
					rover.PressGas()		
					rover.TurnLeft()
					if(rover.rturn):
						rover.DriveFor(0.2)
					else:
						rover.DriveFor(0.1)
					rover.GoStraight()
					rover.ReleaseGas()
					rover.lturn = True
					rover.rturn = False
					rover.DriveFor(1.5)
				else:
					print('Reverse')
					rover.PutInReverse()
					rover.PressGas()
					rover.DriveFor(1)
					rover.ReleaseGas()
					rover.PutInDrive()
					rover.rturn = False
					rover.lturn = False
					rover.DriveFor(1.5)
			else:
				if(rover.rightcone.xMax <= rover.center - 30*(rover.xmax/1920)):
					rover.time = pow((1080/rover.ymax)*rover.rightcone.yMax,-6.055)*129000000000000000
					if(rover.time < 1):
						print("straight")
						rover.GoStraight()
						rover.PressGas()
						rover.DriveFor(1)
						rover.rturn = False
						rover.lturn = False
						rover.TurnLeft()
						rover.DriveFor(0.14)
						rover.ReleaseGas()
						rover.GoStraight()
						rover.DriveFor(1.2)
					else:
						print("Cone straight")
						rover.GoStraight()
						rover.PressGas()
						rover.DriveFor(rover.time)
						rover.rturn = False
						rover.lturn = False
						rover.TurnLeft()
						rover.DriveFor(0.14)
						rover.ReleaseGas()
						rover.GoStraight()
						rover.DriveFor(1.2)
				else:
					print("turn right")
					rover.PressGas()		
					rover.TurnRight()
					rover.DriveFor(0.1)
					rover.GoStraight()
					rover.ReleaseGas()
					rover.rturn = True
					rover.lturn = False
					rover.DriveFor(1.5)
		elif(len(rover.cones) == 1):
			if((len(rover.arucoMarkers) == 0) or rover.am.name == 'AM1'):
				if(rover.cones[0].xMin >= rover.center):
					print("1 cone (right)")
					rover.PressGas()		
					rover.TurnRight()
					if(rover.lturn):
						rover.DriveFor(0.05)
					else:
						rover.DriveFor(0.1)
					rover.GoStraight()
					rover.ReleaseGas()
					rover.rturn = True
					rover.lturn = False
					rover.DriveFor(1.5)
				else:
					print("1 cone (left)")
					rover.PressGas()		
					rover.TurnLeft()
					if(rover.rturn):
						rover.DriveFor(0.05)
					else:
						rover.DriveFor(0.12)
					rover.ReleaseGas()
					rover.GoStraight()
					rover.lturn = True
					rover.rturn = False
					rover.DriveFor(1.5)
			else:
				if(rover.cones[0].xMax <= rover.center):
					rover.time = pow((1080/rover.ymax)*rover.cones[0].yMax ,-6.055)*129000000000000000
					if(rover.time < 1):
						print("straight, one cone")
						rover.GoStraight()
						rover.PressGas()
						rover.DriveFor(1)
						rover.rturn = False
						rover.lturn = False
						rover.TurnLeft()
						rover.DriveFor(0.15)
						rover.ReleaseGas()
						rover.GoStraight()
						rover.DriveFor(1.2)
					else:
						print("Cone straight, one cone")
						rover.GoStraight()
						rover.PressGas()
						rover.DriveFor(rover.time)
						rover.rturn = False
						rover.lturn = False
						rover.TurnLeft()
						rover.DriveFor(0.15)
						rover.ReleaseGas()
						rover.GoStraight()
						rover.DriveFor(1.2)
				else:
					print("1 cone (right)")
					rover.PressGas()		
					rover.TurnRight()
					rover.DriveFor(0.2)
					rover.GoStraight()
					rover.ReleaseGas()
					rover.rturn = True
					rover.lturn = False
					rover.DriveFor(1.5)
		else:
			if(rover.lturn):
				print("no cones (right)")
				rover.PressGas()		
				rover.TurnRight()
				rover.DriveFor(0.3)
				rover.GoStraight()
				rover.ReleaseGas()
				rover.lturn = False
				rover.rturn = True
				rover.DriveFor(1.5)
			else:
				print("no cones (left)")
				rover.PressGas()		
				rover.TurnLeft()
				rover.DriveFor(0.65)
				rover.GoStraight()
				rover.ReleaseGas()
				rover.lturn = True
				rover.rturn = False
				rover.DriveFor(1.5)
		

				
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
