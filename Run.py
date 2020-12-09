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
		
		x_mid = rover.screen.size[0]/2
		print('screen mid:',x_mid)
		y_mid = rover.screen.size[1]/2
		
		cones = []
		arms = []
		
		# adjustable variables
		leftint = 0.6
		rightint = 1.00
		
		print('# of AMs:', len(rover.arucoMarkers), '; # of cones', len(rover.cones))
		
		for arucoMarker in rover.arucoMarkers:
			#print(arucoMarker)
			arm_len = arucoMarker.xMin+(arucoMarker.xMax-arucoMarker.xMin)/2
			arm_area = (arucoMarker.xMax-arucoMarker.xMin)*(arucoMarker.yMax-arucoMarker.yMin)
			arms.append([arucoMarker.name, arm_len, arm_area])
		
		for cone in rover.cones:
			#print(cone)
			cone_len = cone.xMin+(cone.xMax-cone.xMin)/2
			cone_area = (cone.xMax-cone.xMin)*(cone.yMax-cone.yMin)
			cones.append([cone_len, cone_area])
		
		if len(rover.arucoMarkers) >= 1:
			arms.sort(key=lambda x: x[2],reverse=True)
			if arms[0][0] == "AM1":
				arm = 1 # in
			elif arms[0][0] == "AM2":
				arm = 2 # out
		else:
			arm = 0
		print('Marker: ', arm)
		
		if len(rover.cones) >= 2:
			cones.sort(key=lambda x: x[1],reverse=True)
			cone_mid = (cones[0][0]+cones[1][0])/2
			print('cone center:',cone_mid)
			
			if cone_mid <= (x_mid*rightint) and cone_mid >= (x_mid*leftint):
				print('Go Straight')
				rover.PressGas()
				rover.GoStraight().For(2)
				rover.ReleaseGas()
			elif cone_mid < (x_mid*leftint):
				print('Turn Left')
				rover.PressGas()
				rover.TurnLeft().For(0.2)
				rover.GoStraight()
				rover.ReleaseGas()
			elif cone_mid > (x_mid*rightint):
				print('Turn Right')
				rover.PressGas()
				rover.TurnRight().For(0.2)
				rover.GoStraight()
				rover.ReleaseGas()

		elif len(rover.cones)==0 and len(rover.arucoMarkers)==0:
			print('No Cone! Searching...')
			rover.PressGas()
			rover.TurnLeft().For(1)
			rover.GoStraight()
			rover.ReleaseGas()
		
		elif len(rover.cones)==1:
			print('one cone, need action:')
			if len(rover.arucoMarkers) ==0:
				print('Wrong Way!')
				rover.PressGas()
				rover.TurnRight().For(2)
				rover.GoStraight()
				rover.ReleaseGas()
			else:
				if (cones[0][0]) <= (x_mid*0.8):
					print('OverLeft')
					rover.PressGas()
					rover.TurnRight().For(0.6)
					rover.GoStraight()
					rover.ReleaseGas()
				else:
					print('OverRight')
					rover.PressGas()
					rover.TurnLeft().For(0.6)
					rover.GoStraight()
					rover.ReleaseGas()
			
	print(' ')	
		
	def DriveStartUp(rover):
		rover.PressGas()
		rover.GoStraight().For(1.5)
		rover.ReleaseGas()
		# pass
		
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