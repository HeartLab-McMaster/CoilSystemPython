"""
=============================================================================
vision.py
----------------------------------------------------------------------------
Version
1.1.0 2018/08/04 Added snapshot feature.
1.0.0 2018/06/16 Added video writing feature.
0.0.1 2018/02/05 Initial commit
----------------------------------------------------------------------------
[GitHub] : https://github.com/atelier-ritz
=============================================================================
"""


import cv2
import sys
import re
import time
from PyQt5.QtCore import QThread, pyqtSignal
from pydc1394 import Camera
import filterlib
import drawing
import objectDetection
from objectDetection import Agent
from pypylon import pylon
import numpy as np
import traceback  
import datetime


#=============================================================================================
# Mouse callback Functions
#=============================================================================================
def showClickedCoordinate(event,x,y,flags,param):
    # global mouseX,mouseY
    if event == cv2.EVENT_LBUTTONDOWN:
        # mouseX,mouseY = x,y
        print('Clicked position  x: {} y: {}'.format(x,y))




#=============================================================================================
# Camera Thread to handle Basler Pylon Camera in a separate thread
#=============================================================================================
class CameraThread(QThread):
  
    frame_ready = pyqtSignal(object)  

    def __init__(self, camera_index):
        super(CameraThread, self).__init__()
        self.running = False
        self.camera = None
        self.converter = None
        self.camera_index = camera_index  

    def run(self):
       
        try:
            devices = pylon.TlFactory.GetInstance().EnumerateDevices()
            if len(devices) <= self.camera_index:
                raise Exception(f"❌ No camera found at index {self.camera_index}")

           
            selected_device = devices[self.camera_index]
            print(f"✅ Opening camera: {selected_device.GetModelName()}")

          
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(selected_device))
            self.camera.Open()
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

            
            self.converter = pylon.ImageFormatConverter()
            self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

            print(f"✅ Camera {self.camera_index} started grabbing.")
            self.running = True

            while self.running and self.camera.IsGrabbing():
                grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                
               
                if not grabResult.IsValid() or not grabResult.GrabSucceeded():
                    # print(f"⚠️ Camera {self.camera_index}: No valid frame received.")
                    grabResult.Release()
                    continue
                
                
                image = self.converter.Convert(grabResult)
                frame = image.GetArray()
                
                # print(f"📷 Camera {self.camera_index} frame shape: {frame.shape}")

                if self.frame_ready:
                    # print(f"✅ Emitting frame from Camera {self.camera_index}")  # ✅ 确保触发
                    self.frame_ready.emit(frame)
                grabResult.Release()

        except Exception as e:
            print(f"❌ Camera {self.camera_index} error: {e}")
        finally:
            self.stop()
            print(f"✅ Camera {self.camera_index} thread ended.")

    def stop(self):
        
        self.running = False
        if self.camera and self.camera.IsGrabbing():
            self.camera.StopGrabbing()
        if self.camera:
            self.camera.Close()

        self.quit()  
        self.wait()  
        print(f"✅ Camera {self.camera_index} stopped successfully")



class Vision(object):
    def __init__(self,index,type, guid=0000000000000000,buffersize=10):
        self._id = index
        self._type = type
        self._guid = guid
        self._isUpdating = True
        self._isFilterBypassed = True
        self._isObjectDetectionEnabled = False
        self._isSnapshotEnabled = False
        self._detectionAlgorithm = ''
        self.camera_thread = None
        self.filterRouting = [] # data structure: {"filterName", "args"}, defined in the GUI text editor
        # self._camera_index = camera_index  


        # instances of Agent class. You can define an array if you have multiple agents.
        # Pass them to *processObjectDetection()*
        self.agent1 = Agent()
        self.agent2 = Agent()

        # drawings
        self.drawingRouting = [] # data structure: {"drawingName", "args"}, defined in Subthread

        # video writing
        self._isVideoWritingEnabled = False
        self.videoWriter =  None



    def process_frame(self, frame):
 
        if not self._isFilterBypassed and self.filterRouting:
            frame = self.processFilters(frame.copy())

        if self._isObjectDetectionEnabled:
            frame = self.processObjectDetection(frame, frame)

        if self.isDrawingEnabled():
            frame = self.processDrawings(frame)

        if self.isSnapshotEnabled():
            snapshot_frame = frame.copy()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.png"
            cv2.imwrite(filename, filterlib.color(snapshot_frame))
            print(f"✅ snapshot: {filename}")
            self.setStateSnapshotEnabled(False)

       
        if self.isVideoWritingEnabled() and self.videoWriter is not None:
            self.videoWriter.write(filterlib.color(frame))




        return frame  
    
    

    def updateFrame(self):
        pass

        
    #==============================================================================================
    # obtain instance attributes
    #==============================================================================================
    def windowName(self):
        return 'CamID:{} (Click to print coordinate)'.format(self._id)

    def isFireWire(self):
        return self._type.lower() == 'firewire'

    def isUpdating(self):
        return self._isUpdating

    def isFilterBypassed(self):
        return self._isFilterBypassed

    def isObjectDetectionEnabled(self):
        return self._isObjectDetectionEnabled

    def isDrawingEnabled(self):
        return not self.drawingRouting == []

    def isSnapshotEnabled(self):
        return self._isSnapshotEnabled

    def isVideoWritingEnabled(self):
        return self._isVideoWritingEnabled

    #==============================================================================================
    # set instance attributes
    #==============================================================================================
    def setStateUpdate(self,state):
        self._isUpdating = state

    def setStateFiltersBypassed(self,state):
        self._isFilterBypassed = state

    def setStateObjectDetection(self,state,algorithm):
        self._isObjectDetectionEnabled = state
        self._detectionAlgorithm = algorithm

    def setVideoWritingEnabled(self,state):
        self._isVideoWritingEnabled = state

    def setStateSnapshotEnabled(self,state):

        self._isSnapshotEnabled = state
        # print(f"⚡ Snapshot Enabled: {state}")

     

    #==============================================================================================
    # Video recording
    #==============================================================================================
    def createVideoWriter(self,fileName):
        self.videoWriter = cv2.VideoWriter(fileName,fourcc=cv2.VideoWriter_fourcc(*'XVID'),fps=30.0,frameSize=(640,480),isColor=True)

    def startRecording(self,fileName):
        self.createVideoWriter(fileName)
        self.setVideoWritingEnabled(True)
        print('Start recording' + fileName)

    def stopRecording(self):
        self.setStateSnapshotEnabled(False)
        self.videoWriter.release()
        print('Stop recording.')

    #==============================================================================================
    # <Filters>
    # Define the filters in filterlib.py
    #==============================================================================================
    def createFilterRouting(self,text):
        self.filterRouting = []
        for line in text:
            line = line.split('//')[0]  # strip after //
            line = line.strip()         # strip spaces at both ends
            match = re.match(r"(?P<function>[a-z0-9_]+)\((?P<args>.*)\)", line)
            if match:
                name = match.group('function')
                args = match.group('args')
                args = re.sub(r'\s+', '', args) # strip spaces in args
                self.filterRouting.append({'filterName': name, 'args': args})

    def processFilters(self,image):
        for item in self.filterRouting:
            image = getattr(filterlib,item['filterName'],filterlib.filterNotDefined)(image,item['args'])
        # You can add custom filters here if you don't want to use the editor
        return image

    #==============================================================================================
    # <object detection>
    # Object detection algorithm is executed after all the filters
    # It is assumed that "imageFiltered" is used for detection purpose only;
    # the boundary of the detected object will be drawn on "imageOriginal".
    # information of detected objects can be stored in an instance of "Agent" class.
    #==============================================================================================
    def processObjectDetection(self,imageFiltered,imageOriginal):
        # convert to rgb so that coloured lines can be drawn on top
        imageOriginal = filterlib.color(imageOriginal)

        # object detection algorithm starts here
        # In this function, information about the agent will be updated, and the original image with
        # the detected objects highlighted will be returned
        algorithm = getattr(objectDetection,self._detectionAlgorithm,objectDetection.algorithmNotDefined)
        imageProcessed = algorithm(imageFiltered,imageOriginal,self.agent1) # pass instances of Agent class if you want to update its info
        return imageProcessed

    #==============================================================================================
    # <subthread drawing>
    # Used to draw lines etc. on a plot
    # For showing the path that the robot wants to follow
    #==============================================================================================
    def clearDrawingRouting(self):
        self.drawingRouting = []

    def addDrawing(self,name,args=None):
        self.drawingRouting.append({'drawingName': name, 'args': args})

    def processDrawings(self,image):
        # convert to rgb so that coloured lines can be drawn on top
        image = filterlib.color(image)
        for item in self.drawingRouting:
            image = getattr(drawing,item['drawingName'],drawing.drawingNotDefined)(image,item['args'])
        return image