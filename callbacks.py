from PyQt5 import uic
from PyQt5.QtCore import QTimer, Qt, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox
from PyQt5.QtGui import QImage, QPixmap
from fieldManager import FieldManager
from s826 import S826
from subThread import SubThread
from realTimePlot import CustomFigCanvas
import syntax
from vision import Vision
from pypylon import pylon
import cv2
from camera import CameraWindow 

import time
from PS3Controller import DualShock

import pygame

pygame.joystick.init()

try:
    if pygame.joystick.get_count() > 0:
        joystick = DualShock()
        print("✅ Joystick initialized.")
    else:
        raise Exception("No joystick detected")
except Exception as e:
    joystick = None
    print(f"⚠️ No joystick detected: {e}")

#=========================================================
# UI Config
#=========================================================
qtCreatorFile = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


#=========================================================
# Creating instances of fieldManager
#=========================================================
field = FieldManager(S826())


vision1 = Vision(index=1, type='usb')
vision2 = Vision(index=2, type='usb')
vision3 = Vision(index=3, type='usb')

# vision = Vision(index=1, type='usb')
#=========================================================
# a class that handles the signal and callbacks of the GUI
#=========================================================


class GUI(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self, None, Qt.WindowStaysOnTopHint)
        Ui_MainWindow.__init__(self)
        self.updateRate = 10  
        self.setupUi(self)
        self.setupTimer()

        self.setupSubThread(field, vision1, vision2, vision3, joystick)
        self.setupRealTimePlot()
        self.connectSignals()
        self.linkWidgets()
        self._closing = False 
         
        self.camera_window = CameraWindow(field)
        self.camera_window.show()  # 默认显示摄像头窗口

        self.cbb_subThread.clear()
        self.cbb_subThread.addItems(list(self.thrd.labelOnGui.keys()))


  
    def closeEvent(self, event):
        
        self._closing = True
        # print("⚠️ Closing GUI, stopping threads...")


        self.thrd.stop()
        self.timer.stop()

        self.camera_window.close()

        if joystick:
            joystick.quit()

        cv2.destroyAllWindows()

        event.accept()





    #=====================================================
    # QTimer handles updates of the GUI
    #=====================================================
    def setupTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.updateRate)  # msec
        # print(f"✅ Timer started with update rate {self.updateRate}ms")
     

    def update(self):
        vision1.updateFrame()
        vision2.updateFrame()
        vision3.updateFrame() 

   
        if joystick:
            joystick.update()
     

        try:
            self.realTimePlot
        except AttributeError:
            pass
        else:
            self.updatePlot()

    #=====================================================
    # Connect buttons etc. of the GUI to callback functions

    #=====================================================
    def connectSignals(self):
        # print("✅ Checking dsb_x, dsb_y, dsb_z...")
        # print(f"dsb_x: {self.dsb_x}, dsb_y: {self.dsb_y}, dsb_z: {self.dsb_z}")  
        self.dsb_x.valueChanged.connect(self.setFieldXYZ)
        self.dsb_y.valueChanged.connect(self.setFieldXYZ)
        self.dsb_z.valueChanged.connect(self.setFieldXYZ)
        # self.setFieldXYZ()
        self.btn_clearCurrent.clicked.connect(self.clearField)
        self.dsb_xGradient.valueChanged.connect(self.setFieldXYZGradient)
        self.dsb_yGradient.valueChanged.connect(self.setFieldXYZGradient)
        self.dsb_zGradient.valueChanged.connect(self.setFieldXYZGradient)

        self.highlighter = syntax.Highlighter(self.editor_vision.document())
        self.chb_bypassFilters.toggled.connect(self.on_chb_bypassFilters)
        self.btn_refreshFilterRouting.clicked.connect(self.on_btn_refreshFilterRouting)
        self.btn_snapshot.clicked.connect(self.on_btn_snapshot)

        # object detection
        self.chb_objectDetection.toggled.connect(self.on_chb_objectDetection)

        # Subthread Tab
        self.cbb_subThread.currentTextChanged.connect(self.on_cbb_subThread)
        self.chb_startStopSubthread.toggled.connect(self.on_chb_startStopSubthread)
        self.dsb_subThreadParam0.valueChanged.connect(self.thrd.setParam0)
        self.dsb_subThreadParam1.valueChanged.connect(self.thrd.setParam1)
        self.dsb_subThreadParam2.valueChanged.connect(self.thrd.setParam2)
        self.dsb_subThreadParam3.valueChanged.connect(self.thrd.setParam3)
        self.dsb_subThreadParam4.valueChanged.connect(self.thrd.setParam4)

    #=====================================================
    # Link GUI elements
    #=====================================================
    def linkWidgets(self):
        self.dsb_x.valueChanged.connect(lambda value: self.hsld_x.setValue(int(value * 100)))
        self.dsb_y.valueChanged.connect(lambda value: self.hsld_y.setValue(int(value * 100)))
        self.dsb_z.valueChanged.connect(lambda value: self.hsld_z.setValue(int(value * 100)))
        self.hsld_x.valueChanged.connect(lambda value: self.dsb_x.setValue(float(value / 100)))
        self.hsld_y.valueChanged.connect(lambda value: self.dsb_y.setValue(float(value / 100)))
        self.hsld_z.valueChanged.connect(lambda value: self.dsb_z.setValue(float(value / 100)))

        self.dsb_xGradient.valueChanged.connect(lambda value: self.hsld_xGradient.setValue(int(value*100)))
        self.dsb_yGradient.valueChanged.connect(lambda value: self.hsld_yGradient.setValue(int(value*100)))
        self.dsb_zGradient.valueChanged.connect(lambda value: self.hsld_zGradient.setValue(int(value*100)))
        self.hsld_xGradient.valueChanged.connect(lambda value: self.dsb_xGradient.setValue(float(value/100)))
        self.hsld_yGradient.valueChanged.connect(lambda value: self.dsb_yGradient.setValue(float(value/100)))
        self.hsld_zGradient.valueChanged.connect(lambda value: self.dsb_zGradient.setValue(float(value/100)))
    
    def setupSubThread(self, field, vision1, vision2, vision3, joystick=None):
        if joystick:
            self.thrd = SubThread(field, vision1, vision2, vision3, joystick)
        else:
            self.thrd = SubThread(field, vision1, vision2, vision3)
        
        self.thrd.statusSignal.connect(self.updateSubThreadStatus)
        self.thrd.finished.connect(self.finishSubThreadProcess)



    @pyqtSlot(str)
    def updateSubThreadStatus(self, receivedStr):
        print('Received message from subthread: ', receivedStr)

    @pyqtSlot()
    def finishSubThreadProcess(self):
        print('Subthread is terminated.')
        vision1.clearDrawingRouting()
        vision2.clearDrawingRouting()
        vision3.clearDrawingRouting()
        self.clearField()

    #=====================================================
    # Real time plot
    #=====================================================
    def setupRealTimePlot(self):
        self.realTimePlot = CustomFigCanvas()
        print("✅ realTimePlot created") 
        self.LAYOUT_A.addWidget(self.realTimePlot, *(0, 0))
        self.btn_zoom.clicked.connect(self.realTimePlot.zoom)

 

    def updatePlot(self):
        self.realTimePlot.addDataX(field.x)
        self.realTimePlot.addDataY(field.y)
        self.realTimePlot.addDataZ(field.z)
  

    #=====================================================
    # Callback Functions
    #=====================================================
    def setFieldXYZ(self):
        # field.setX(self.dsb_x.value())
        # field.setY(self.dsb_y.value())
        # field.setZ(self.dsb_z.value())
        field.setXYZ(self.dsb_x.value(),self.dsb_y.value(),self.dsb_z.value())

    def clearField(self):
        self.dsb_x.setValue(0)
        self.dsb_y.setValue(0)
        self.dsb_z.setValue(0)
        self.dsb_xGradient.setValue(0)
        self.dsb_yGradient.setValue(0)
        self.dsb_zGradient.setValue(0)
        # field.setXYZ(0, 0, 0)

    def setFieldXYZGradient(self):
        field.setXGradient(self.dsb_xGradient.value())
        field.setYGradient(self.dsb_yGradient.value())
        field.setZGradient(self.dsb_zGradient.value())


    # vision tab
    def on_chb_bypassFilters(self, state):

        vision1.setStateFiltersBypassed(state)
        vision2.setStateFiltersBypassed(state)
        vision3.setStateFiltersBypassed(state)


    def on_btn_refreshFilterRouting(self):

        # filter_text = self.editor_vision.toPlainText().splitlines()
        vision1.createFilterRouting(self.editor_vision.toPlainText().splitlines())
        vision2.createFilterRouosc_sinting(self.editor_vision.toPlainText().splitlines())
        vision3.createFilterRouting(self.editor_vision.toPlainText().splitlines())


    def on_btn_snapshot(self):

        vision1.setStateSnapshotEnabled(True)
        vision2.setStateSnapshotEnabled(True)
        vision3.setStateSnapshotEnabled(True)


    def on_chb_objectDetection(self, state):

        algorithm = self.cbb_objectDetectionAlgorithm.currentText()
        vision1.setStateObjectDetection(state, algorithm)
        vision2.setStateObjectDetection(state, algorithm)
        vision3.setStateObjectDetection(state, algorithm)

        self.cbb_objectDetectionAlgorithm.setEnabled(not state)

    # subthread
    def on_cbb_subThread(self,subThreadName):
        # an array that stores the name for params. Return param0, param1, ... if not defined.
        labelNames = self.thrd.labelOnGui.get(subThreadName,self.thrd.labelOnGui['default'])
        minVals = self.thrd.minOnGui.get(subThreadName,self.thrd.minOnGui['default'])
        maxVals = self.thrd.maxOnGui.get(subThreadName,self.thrd.maxOnGui['default'])
        defaultVals = self.thrd.defaultValOnGui.get(subThreadName,self.thrd.defaultValOnGui['default'])
        for i in range(5):
            targetLabel = 'lbl_subThreadParam' + str(i)
            targetSpinbox = 'dsb_subThreadParam' + str(i)
            getattr(self,targetLabel).setText(labelNames[i])
            getattr(self,targetSpinbox).setMinimum(minVals[i])
            getattr(self,targetSpinbox).setMaximum(maxVals[i])
    
            getattr(self,targetSpinbox).setValue(defaultVals[i])
    


    def on_chb_startStopSubthread(self,state):
        subThreadName = self.cbb_subThread.currentText()
        if state:
            self.cbb_subThread.setEnabled(False)
            self.thrd.setup(subThreadName)
            self.thrd.start()
            print('Subthread "{}" starts.'.format(subThreadName))
        else:
            self.cbb_subThread.setEnabled(True)
            self.thrd.stop()