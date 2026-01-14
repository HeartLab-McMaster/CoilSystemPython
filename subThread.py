"""
=============================================================================
subThread.py
----------------------------------------------------------------------------
Tips
If you are using Atom, use Ctrl+Alt+[ to fold all the funcitons.
Make your life easier.
----------------------------------------------------------------------------
[GitHub] : https://github.com/atelier-ritz
=============================================================================
"""
import time
from mathfx import *
from math import pi, sin, cos, sqrt, atan2, degrees
from PyQt5.QtCore import pyqtSignal, QMutexLocker, QMutex, QThread
import csv
import pandas as pd
import os

def subthreadNotDefined():
    print('Subthread not defined.')
    return

class SubThread(QThread):
    statusSignal = pyqtSignal(str)

    def __init__(self,field,vision1, vision2, vision3, joystick=None,parent=None,):
        super(SubThread, self).__init__(parent)
        self.stopped = False
        
        self.mutex = QMutex()
        self.field = field
        # self.vision = vision
        self.vision1 = vision1  
        self.vision2 = vision2  
        self.vision3 = vision3  
        self.joystick = joystick
        self._subthreadName = ''
        self.running = True
        self.params = [0,0,0,0,0]
        self.labelOnGui = {'twistField': ['Frequency (Hz)','Magniude (mT)','AzimuthalAngle (deg)','PolarAngle (deg)','SpanAngle (deg)'],
                        'rotateXY': ['Frequency (Hz)','Magnitude-X (mT)','Magnitude-Y (mT)','N/A','N/A'],
                        'rotateYZ': ['Frequency (Hz)','Magnitude-Y (mT)','Magnitude-Z (mT)','N/A','N/A'],
                        'rotateXZ': ['Frequency (Hz)','Magnitude-X (mT)','Magnitude-Z (mT)','N/A','N/A'],
                        'osc_saw': ['Frequency (Hz)','bound1 (mT)','bound2 (mT)','Azimuth [0,360] (deg)','Polar [-90,90] (deg)'],
                        'osc_triangle': ['Frequency (Hz)','bound1 (mT)','bound2 (mT)','Azimuth [0,360] (deg)','Polar [-90,90] (deg)'],
                        'osc_square': ['Frequency (Hz)','bound1 (mT)','bound2 (mT)','Azimuth [0,360] (deg)','Polar [-90,90] (deg)'],
                        'osc_sin': ['Frequency (Hz)','bound1 (mT)','bound2 (mT)','Azimuth [0,360] (deg)','Polar [-90,90] (deg)'],
                        'osc_cos': ['Frequency (Hz)','bound1 (mT)','bound2 (mT)','Azimuth [0,360] (deg)','Polar [-90,90] (deg)'],
                        'oni_cutting': ['Frequency (Hz)','Magnitude (mT)','angleBound1 (deg)','angleBound2 (deg)','N/A'],
                        'examplePiecewiseFunction': ['Frequency (Hz)','Magnitude (mT)','angle (deg)','period1 (0-1)','period2 (0-1)'],
                        'ellipse': ['Frequency (Hz)','Azimuthal Angle (deg)','B_horzF (mT)','B_vert (mT)','B_horzB (mT)'],
                        'drawing': ['pattern ID','offsetX','offsetY','N/A','N/A'],
                        'swimmerPathFollowing': ['Frequency (Hz)','Magniude (mT)','temp angle','N/A','N/A'],
                        'swimmerBenchmark': ['bias angle (deg)','N/A','N/A','N/A','N/A'],
                        'tianqiGripper': ['N/A','Magnitude (mT)','Frequency (Hz)','Direction (deg)','N/A'],
                        'fromCSV': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
                        'formulaControlledField': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
                        'crawler_walking': ['Bmax (mT)', 'Frequency (Hz)', 'Max2'],
                        'xy_angle': ['Magnitude (mT)', 'Angle (deg)','N/A','N/A','N/A'],
                        'default':['param0','param1','param2','param3','param4']}
        self.defaultValOnGui = {
                        'twistField': [0,0,0,0,0],
                        'drawing': [0,0,0,1,0],
                        'swimmerPathFollowing': [-20,2,0,0,0],
                        'tianqiGripper': [0,15,0.5,0,0],
                        'fromCSV': [0, 0, 0, 0, 0],
                        'formulaControlledField': [0, 0, 0, 0, 0],
                        'crawler_walking': [5, 5, 5],
                        'default':[0,0,0,0,0]
                        }
        self.minOnGui = {'twistField': [-100,0,-1080,0,0],
                        'rotateXY': [-100,-25,-25,-25,-25],
                        'rotateYZ': [-100,-25,-25,-25,-25],
                        'rotateXZ': [-100,-25,-25,-25,-25],
                        'osc_saw': [-100,-20,-20,0,-90],
                        'osc_triangle': [-100,-20,-20,0,-90],
                        'osc_square': [-100,-20,-20,0,-90],
                        'osc_sin': [-100,-20,-20,0,-90],
                        'osc_cos': [-100, -20, -20, 0, -90],
                        'oni_cutting': [-100,-25,-720,-720,0],
                        'ellipse': [-100,-720,0,0,0],
                        'examplePiecewiseFunction': [-20,0,-360,0,0],
                        'swimmerPathFollowing': [-100,0,0,0,0],
                        'tianqiGripper': [0,0,0,-720,0],
                        'fromCSV': [0, 0, 0, 0, 0],
                        'formulaControlledField': [0, 0, 0, 0, 0],
                        'crawler_walking': [-50, 0, -50],
                        'xy_angle': [-50, 0, -50],
                        'default':[0,0,0,0,0]}
        self.maxOnGui = {'twistField': [100,25,1080,180,360],
                        'rotateXY': [100,25,25,25,25],
                        'rotateYZ': [100,25,25,25,25],
                        'rotateXZ': [100,25,25,25,25],
                        'osc_saw': [100,20,20,360,90],
                        'osc_triangle': [100,20,20,360,90],
                        'osc_square': [100,20,20,360,90],
                        'osc_sin': [100,20,20,360,90],
                        'osc_cos': [100, 20, 20, 360, 90],
                        'oni_cutting': [100,25,720,720,0],
                        'ellipse': [100,720,20,20,20],
                        'examplePiecewiseFunction': [20,20,360,1,1],
                        'drawing':[2,1000,1000,10,0],
                        'swimmerPathFollowing': [100,20,360,0,0],
                        'swimmerBenchmark': [360,0,0,0,0],
                        'tianqiGripper': [10,20,120,720,0],
                        'fromCSV': [0, 0, 0, 0, 0],
                        'formulaControlledField': [0, 0, 0, 0, 0],
                        'crawler_walking': [50, 10, 50],
                        'xy_angle': [50, 360, 50],
                        'default':[0,0,0,0,0]}

    def setup(self,subThreadName):
        self._subthreadName = subThreadName
        self.stopped = False

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def run(self):
        
        # while self.running:  # 让线程持续运行
        #     print(f"Current Field Values -> X: {self.field.x}, Y: {self.field.y}, Z: {self.field.z}")  # 打印电流数值
        #      # ✅ 处理 3 个摄像头的帧
        #     if self.vision1:     
        #         frame1 = self.vision1.updateFrame()
        #     if self.vision2:
        #         frame2 = self.vision2.updateFrame()
        #     if self.vision3:
        #         frame3 = self.vision3.updateFrame()
                
            # time.sleep(1)  # 每秒打印一次，避免刷屏过快
        self.stopped = False
        subthreadFunction = getattr(self,self._subthreadName,subthreadNotDefined)
        subthreadFunction()

    def setParam0(self,val): 
        self.params[0] = val
        # print(f"param0 被设置为 {val}")
    def setParam1(self,val): self.params[1] = val
    def setParam2(self,val): self.params[2] = val
    def setParam3(self,val): self.params[3] = val
    def setParam4(self,val): self.params[4] = val

    #=========================================
    # Start defining your subthread from here
    #=========================================
    def drawing(self):
        """
        An example of drawing lines and circles in a subThread
        (Not in object detection)
        """
        #=============================
        # reference params
        # 0 'Path ID'
        # 1 'offsetX'
        # 2 'offsetY'
        # 3 'scale'
        #=============================
        startTime = time.time()
        # video writing feature
        # self.vision.startRecording('drawing.avi')
           # ✅ Start video recording for all 3 cameras
        self.vision1.startRecording('drawing1.avi')
        self.vision2.startRecording('drawing2.avi')
        self.vision3.startRecording('drawing3.avi')

        while True:
            # ✅ Clear drawings for all 3 cameras
            for vision in [self.vision1, self.vision2, self.vision3]:
                if vision:
                    vision.clearDrawingRouting()
                # ✅ Add drawings for all 3 cameras
            for vision in [self.vision1, self.vision2, self.vision3]:
                if vision:
                    vision.addDrawing('pathUT', self.params)
                    vision.addDrawing('circle', [420, 330, 55])
                    vision.addDrawing('arrow', [0, 0, 325, 325])
            # you can also do somthing like:
            # drawing an arrow from "the robot" to "the destination point"
            t = time.time() - startTime # elapsed time (sec)
            self.field.setX(0)
            self.field.setY(0)
            self.field.setZ(0)
            if self.stopped:
                print("✅ Stopping drawing thread and saving recordings.")
                self.vision1.stopRecording()
                self.vision2.stopRecording()
                self.vision3.stopRecording()
                return

    def swimmerPathFollowing(self):
        '''
        An example of autonomous path following of a sinusoidal swimmer at air-water interface.
        This example follows the path "M".
        '''
        #=============================
        # Reference params:
        # 0 'Frequency (Hz)'
        # 1 'Magnitude (mT)'
        # 2 'Temp angle'
        #=============================

        # Start video recording for all 3 cameras
        self.vision1.startRecording('path1.avi')
        self.vision2.startRecording('path2.avi')
        self.vision3.startRecording('path3.avi')

        startTime = time.time()
        state = 0  # Indicates which goal point the robot is approaching
        rect = [640, 480]  # Image size in pixels
        pointsX = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]  # Normalized X positions
        pointsY = [0.7, 0.3, 0.3, 0.7, 0.3, 0.3, 0.7]  # Normalized Y positions
        goalsX = [int(rect[0] * i) for i in pointsX]  # Convert to pixel positions
        goalsY = [int(rect[1] * i) for i in pointsY]

        tolerance = 10  # Distance threshold to consider reaching a goal
        toleranceDeviation = 30  # Threshold for path correction
        magnitudeCorrection = 1  # Factor to avoid overshooting near goals

        while True:
            # =============================
            # Get robot position from all 3 cameras
            # =============================
            positions = []
            for vision in [self.vision1, self.vision2, self.vision3]:
                if vision and hasattr(vision, "agent1"):
                    positions.append((vision.agent1.x, vision.agent1.y))
            
            if not positions:  # 如果所有摄像头都没有检测到目标
                print("⚠️ Warning: No valid positions detected from any camera!")
                continue

            # 计算 3 个摄像头的均值作为机器人位置，减少单个摄像头误差
            x = sum(pos[0] for pos in positions) / len(positions)
            y = sum(pos[1] for pos in positions) / len(positions)

            # 获取当前目标点
            goalX = goalsX[state]
            goalY = goalsY[state]

            # 只有 `state > 0` 时才访问 `goalXPrevious`
            if state > 0:
                goalXPrevious = goalsX[state - 1]
                goalYPrevious = goalsY[state - 1]
            else:
                goalXPrevious = goalX
                goalYPrevious = goalY

            # =============================
            # Draw reference lines on all 3 cameras
            # =============================
            for vision in [self.vision1, self.vision2, self.vision3]:
                if vision:
                    vision.clearDrawingRouting()  # 防止绘图数据累积
                    vision.addDrawing('closedPath', [goalsX, goalsY])
                    vision.addDrawing('circle', [goalX, goalY, 5])
                    vision.addDrawing('line', [x, y, goalX, goalY])

            # =======================================================
            # Calculate heading angle for movement
            # =======================================================
            distance = distanceBetweenPoints(x, y, goalX, goalY)
            footX, footY = perpendicularFootToLine(x, y, goalXPrevious, goalYPrevious, goalX, goalY)
            deviation = distanceBetweenPoints(x, y, footX, footY)

            if deviation > toleranceDeviation:
                # Move perpendicular to the reference path
                angle = degrees(atan2(-(footY - y), footX - x))
            else:
                angleRobotToGoal = atan2(-(goalY - y), goalX - x)
                angleRobotToFoot = atan2(-(footY - y), footX - x)
                angleCorrectionOffset = normalizeAngle(angleRobotToFoot - angleRobotToGoal) * deviation / toleranceDeviation
                angle = degrees(angleRobotToGoal + angleCorrectionOffset)

            # Reduce speed near the target
            magnitudeCorrection = 0.5 if distance <= tolerance * 3 else 1

            # =============================
            # Check if the goal is reached
            # =============================
            if distance <= tolerance:
                state += 1
                print(f'>>> Step to point {state} <<<')

            # =============================
            # Apply magnetic field
            # =============================
            t = time.time() - startTime
            theta = 2 * pi * self.params[0] * t
            fieldX = magnitudeCorrection * self.params[1] * cos(theta) * cosd(angle + self.params[2])
            fieldY = magnitudeCorrection * self.params[1] * cos(theta) * sind(angle + self.params[2])
            fieldZ = magnitudeCorrection * self.params[1] * sin(theta)
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)

            # =============================
            # Stop condition: All points reached
            # =============================
            if self.stopped or state >= len(pointsX):
                print("✅ Path following complete. Stopping all recordings.")
                self.vision1.stopRecording()
                self.vision2.stopRecording()
                self.vision3.stopRecording()
                return

    def tianqiGripper(self):
        #=============================
        # reference params
        # 0 'N/A'
        # 1 'Magnitude (mT)'
        # 2 'Frequency (Hz)'
        #=============================

        # ''' Video Recording '''
        # self.vision.startRecording('TianqiGripper.avi')
        ''' Init '''
        startTime = time.time()
        paramSgnMagZ = 1 # use R1 button to change the sign of Z magnitude
        paramFieldScale = 1 # change the field strength with R2
        ''' Rotating the gripper '''
        paramRotationOffsetTime = 0 # used to avoid sudden changes while switching to rotating mode
        paramRotationPhase = 0 # used for MODE3 - Fine rotation control
        ''' Modes '''
        mode = 0 # change the mode with buttons on PS3 controller
        BUTTON_RESPONSE_TIME = 0.2 # at least 0.2 sec between button triggers
        lastButtonPressedTimeMode = 0
        lastButtonPressedTimeR1 = 0 # the last time that the user changing the mode

        while True:
            t = time.time() - startTime # elapsed time (sec)
            # =======================================================
            # Detect Button Pressed to Change the MODE
            # =======================================================
            if t - lastButtonPressedTimeMode > BUTTON_RESPONSE_TIME:
                if self.joystick.isPressed('CROSS') and not mode == 0:
                    lastButtonPressedTimeMode = t
                    mode = 0
                    print('[MODE] Standby')
                elif self.joystick.isPressed('CIRCLE') and not mode == 1:
                    lastButtonPressedTimeMode = t
                    mode = 1
                    print('[MODE] Grasp')
                elif self.joystick.isPressed('TRIANGLE') and not mode == 2:
                    lastButtonPressedTimeMode = t
                    mode = 2
                    print('[MODE] Transport Auto')
                    paramRotationOffsetTime = t
                elif self.joystick.isPressed('SQUARE') and not mode == 3:
                    lastButtonPressedTimeMode = t
                    mode = 3
                    print('[MODE] Transport Manual')
                    paramRotationPhase = pi / 2
            # =======================================================
            # Flip direction of Z field
            # =======================================================
            if t - lastButtonPressedTimeR1 > BUTTON_RESPONSE_TIME:
                if self.joystick.isPressed('R1'):
                    lastButtonPressedTimeR1 = t
                    paramSgnMagZ = - paramSgnMagZ
                    print('The sign of fieldZ is {}'.format(paramSgnMagZ))
            # =======================================================
            # change magnitude of field with R2
            # =======================================================
            rawR2 = self.joystick.getStick(5) # -1 -> 1
            paramFieldScale = 0.5 * (- rawR2 + 1)
            # =======================================================
            # Process fieldXYZ in each mode
            # =======================================================
            if mode == 0:
                fieldX = 0
                fieldY = 0
                fieldZ = 0
            elif mode == 1:
                polar = self.joystick.getTiltLeft()
                azimuth = self.joystick.getAngleLeft()
                fieldX = self.params[1] * cosd(polar) * cosd(azimuth)
                fieldY = self.params[1] * cosd(polar) * sind(azimuth)
                fieldZ = self.params[1] * sind(polar)
            elif mode == 2:
                theta = - 2 * pi * self.params[2] * (t - paramRotationOffsetTime) + pi / 2
                fieldX = self.params[1] * cos(theta) * cosd(self.joystick.getAngleLeft())
                fieldY = self.params[1] * cos(theta) * sind(self.joystick.getAngleLeft())
                fieldZ = self.params[1] * sin(theta)
            elif mode == 3:
                if t - lastButtonPressedTimeMode > BUTTON_RESPONSE_TIME:
                    if self.joystick.isPressed('SQUARE'):
                        lastButtonPressedTimeMode = t
                        if self.joystick.isPressed('L1'):
                            paramRotationPhase = paramRotationPhase + pi/16
                        else:
                            paramRotationPhase = paramRotationPhase - pi/16
                fieldX = self.params[1] * cos(paramRotationPhase) * cosd(self.joystick.getAngleLeft())
                fieldY = self.params[1] * cos(paramRotationPhase) * sind(self.joystick.getAngleLeft())
                fieldZ = self.params[1] * sin(paramRotationPhase)

            self.field.setX(fieldX * paramFieldScale)
            self.field.setY(fieldY * paramFieldScale)
            self.field.setZ(fieldZ * paramFieldScale * paramSgnMagZ)
            if self.stopped:
                # self.vision.stopRecording()
                return

    def swimmerBenchmark(self):
        '''
        Benchmarking swimmer velocity with respect to frequency and magnitude.
        It demonstrates:
            - Path following: Point0 -> Point1 -> Point0
            - Repeating the task for different frequencies
            - Drawing real-time reference lines and target markers
        '''
        # ✅ Start video recording for all 3 cameras
        self.vision1.startRecording('benchmark1.avi')
        self.vision2.startRecording('benchmark2.avi')
        self.vision3.startRecording('benchmark3.avi')

        startTime = time.time()
        state = 0  # Current target point
        freq = [-15, -15, -17, -19, -21, -23, -25]  # Frequencies
        freq = [i - 8 for i in freq]  # Adjusted frequency offset
        magnitude = 8
        benchmarkState = 0  # Current frequency being tested

        rect = [640, 480]  # Image size
        pointsX = [0.2, 0.8]  # Normalized X positions
        pointsY = [0.2, 0.8]  # Normalized Y positions
        goalsX = [int(rect[0] * i) for i in pointsX]  # Convert to pixels
        goalsY = [int(rect[1] * i) for i in pointsY]

        tolerance = 20  # Distance threshold to reach a goal

        print(f'Moving to the home position. Frequency {freq[benchmarkState]} Hz')

        while True:
            # =============================
            # Get robot position from all 3 cameras
            # =============================
            positions = []
            for vision in [self.vision1, self.vision2, self.vision3]:
                if vision and hasattr(vision, "agent1"):
                    positions.append((vision.agent1.x, vision.agent1.y))

            if not positions:
                print("⚠️ Warning: No valid positions detected from any camera!")
                continue  # Skip this iteration if no valid positions

            # Calculate averaged position from multiple cameras
            x = sum(pos[0] for pos in positions) / len(positions)
            y = sum(pos[1] for pos in positions) / len(positions)

            # Get current target point
            goalX = goalsX[state]
            goalY = goalsY[state]

            # =============================
            # Draw reference lines on all 3 cameras
            # =============================
            for vision in [self.vision1, self.vision2, self.vision3]:
                if vision:
                    vision.clearDrawingRouting()
                    vision.addDrawing('closedPath', [goalsX, goalsY])
                    vision.addDrawing('circle', [goalX, goalY, 5])
                    vision.addDrawing('line', [x, y, goalX, goalY])

            # =============================
            # Calculate distance and angle
            # =============================
            distance = sqrt((goalX - x) ** 2 + (goalY - y) ** 2)
            angle = degrees(atan2(-(goalY - y), goalX - x))  # Convert to degrees

            # =============================
            # Check if the goal is reached
            # =============================
            if distance <= tolerance:
                if state == 0:
                    benchmarkState += 1
                    if benchmarkState < len(freq):
                        print(f'Case {benchmarkState} - Benchmark Frequency {freq[benchmarkState]} Hz')

                state += 1  # Move to next goal
                if state == len(pointsX):
                    state = 0  # Reset path if completed

                if benchmarkState < len(freq):
                    print(f'    >>> Step to point {state} <<<')

            # =============================
            # Apply magnetic field
            # =============================
            t = time.time() - startTime
            theta = 2 * pi * freq[benchmarkState] * t
            fieldX = magnitude * cos(theta) * cosd(angle + self.params[0])
            fieldY = magnitude * cos(theta) * sind(angle + self.params[0])
            fieldZ = magnitude * sin(theta)

            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)

            # =============================
            # Stop condition: All frequencies tested
            # =============================
            if self.stopped or benchmarkState == len(freq):
                print("✅ Benchmark complete. Stopping all recordings.")
                self.vision1.stopRecording()
                self.vision2.stopRecording()
                self.vision3.stopRecording()
                return

    def examplePiecewiseFunction(self):
        """
        This function shows an example of a piecewise function.
        It first convert time into normalizedTime (range [0,1)).
        Values are selected based on *normT*.
        This makes it easier to change frequency without modifying the shape of the funciton.
        """
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Magnitude (mT)'
        # 2 'angle (deg)'
        # 3 'period1 (0-1)'
        # 4 'period2 (0-1)'
        #=============================
        startTime = time.time()

        while True:
            t = time.time() - startTime # elapsed time (sec)
            normT = normalizeTime(t,self.params[0]) # 0 <= normT < 1
            if normT < self.params[3]:
                magnitude = self.params[1] / oscX_sawself.params[3] * normT
                angle = 180
            elif normT < self.params[4]:
                magnitude = self.params[1]
                angle = (180 - self.params[2])/(self.params[3] - self.params[4]) * (normT - self.params[3]) + 180
            else:
                magnitude = self.params[1] / (self.params[4] - 1) * (normT - 1)
                angle = self.params[2]
            fieldX = magnitude * sind(angle)
            fieldY = 0
            fieldZ = magnitude * cosd(angle)
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)
            if self.stopped:
                return

    def ellipse(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'azimuth (deg)'
        # 2 'B_horzF (mT)'
        # 3 'B_vert (mT)'
        # 4 'B_horzB (mT)'
        #=============================
        startTime = time.time()
        counter = 0
        record = ''
        while True:
            t = time.time() - startTime # elapsed time (sec)
            theta = 2 * pi * self.params[0] * t
            normT = normalizeTime(t,self.params[0]) # 0 <= normT < 1
            if normT < 0.5:
                B_horz = self.params[2] * cos(theta)
            else:
                B_horz = self.params[4] * cos(theta)
            fieldX = B_horz * cosd(self.params[1])
            fieldY = B_horz * sind(self.params[1])
            fieldZ = self.params[3] * sin(theta)
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)
            # save to txt
            counter += 1
            if counter > 10:
                counter = 0
                record = record + '{:.5f}, {:.2f}, {:.2f}, {:.2f}, {}, {}\n'.format(t,self.field.x,self.field.y,self.field.z,self.vision.agent1.x,self.vision.agent1.y)
            if self.stopped:
                text_file = open("Output.txt", "w")
                text_file.write(record)
                text_file.close()
                return

    def oni_cutting(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Magnitude (mT)'
        # 2 'angleBound1 (deg)'
        # 3 'angleBound2 (deg)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            angle = oscBetween(t,'sin',self.params[0],self.params[2],self.params[3])
            fieldX = self.params[1] * cosd(angle)
            fieldY = self.params[1] * sind(angle)
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(0)
            if self.stopped:
                return

    def twistField(self):
        ''' credit to Omid '''
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Magniude (mT)'
        # 2 'AzimuthalAngle (deg)'
        # 3 'PolarAngle (deg)'
        # 4 'SpanAngle (deg)'
        #=============================
        startTime = time.time()
        record = 'Time(s), FieldX(mT), FiledY(mT), FieldZ(mT), X(pixel), Y(pixel) \n' # output to a txt file
        counter = 0
        while True:
            t = time.time() - startTime # elapsed time (sec)
            fieldX = self.params[1]* ( cosd(self.params[2])*cosd(self.params[3])*cosd(90-self.params[4]*0.5)*cos(2*pi*self.params[0]*t) - sind(self.params[2])*cosd(90-self.params[4]*0.5)*sin(2*pi*self.params[0]*t) + cosd(self.params[2])*sind(self.params[3])*cosd(self.params[4]*0.5));
            fieldY = self.params[1]* ( sind(self.params[2])*cosd(self.params[3])*cosd(90-self.params[4]*0.5)*cos(2*pi*self.params[0]*t) + cosd(self.params[2])*cosd(90-self.params[4]*0.5)*sin(2*pi*self.params[0]*t) + sind(self.params[2])*sind(self.params[3])*cosd(self.params[4]*0.5));
            fieldZ = self.params[1]* (-sind(self.params[3])*cosd(90-self.params[4]*0.5)*cos(2*pi*self.params[0]*t) + cosd(self.params[3])*cosd(self.params[4]*0.5));
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)
            # save to txt
            counter += 1
            if counter > 300:
                counter = 0
                record = record + '{:.5f}, {:.2f}, {:.2f}, {:.2f}, {}, {}\n'.format(t,self.field.x,self.field.y,self.field.z,self.vision.agent1.x,self.vision.agent1.y)
            if self.stopped:
                text_file = open("Output.txt", "w")
                text_file.write(record)
                text_file.close()
                return

    def osc_saw(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Lowerbound (mT)'
        # 2 'Upperbound (mT)'
        # 3 'Azimuthal Angle (deg)'
        # 4 'Polar Angle (deg)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            magnitude = oscBetween(t,'saw',self.params[0],self.params[1],self.params[2])
            fieldZ = magnitude * sind(self.params[4])
            fieldX = magnitude * cosd(self.params[4]) * cosd(self.params[3])
            fieldY = magnitude * cosd(self.params[4]) * sind(self.params[3])
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)
            if self.stopped:
                return

    def osc_triangle(self):
        #=============================
        # reference params(200,255)
        # 0 'Frequency (Hz)'
        # 1 'Lowerbound (mT)'
        # 2 'Upperbound (mT)'
        # 3 'Azimuthal Angle (deg)'
        # 4 'Polar Angle (deg)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            magnitude = oscBetween(t,'triangle',self.params[0],self.params[1],self.params[2])
            fieldZ = magnitude * sind(self.params[4])
            fieldX = magnitude * cosd(self.params[4]) * cosd(self.params[3])
            fieldY = magnitude * cosd(self.params[4]) * sind(self.params[3])
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)
            if self.stopped:
                return

    def osc_square(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Lowerbound (mT)'
        # 2 'Upperbound (mT)'
        # 3 'Azimuthal Angle (deg)'
        # 4 'Polar Angle (deg)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            magnitude = oscBetween(t,'square',self.params[0],self.params[1],self.params[2])
            fieldZ = magnitude * sind(self.params[4])
            fieldX = magnitude * cosd(self.params[4]) * cosd(self.params[3])
            fieldY = magnitude * cosd(self.params[4]) * sind(self.params[3])
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)
            if self.stopped:
                return

    def osc_sin(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Lowerbound (mT)'
        # 2 'Upperbound (mT)'
        # 3 'Azimuthal Angle (deg)'
        # 4 'Polar Angle (deg)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            magnitude = oscBetween(t,'sin',self.params[0],self.params[1],self.params[2])
            fieldZ = magnitude * sind(self.params[4])
            fieldX = magnitude * cosd(self.params[4]) * cosd(self.params[3])
            fieldY = magnitude * cosd(self.params[4]) * sind(self.params[3])
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)
           
      
            # time.sleep(1/2000)  # 控制刷新速率，避免 CPU 飙高

            if self.stopped:
                return
    def osc_cos(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Lowerbound (mT)'
        # 2 'Upperbound (mT)'
        # 3 'Azimuthal Angle (deg)'
        # 4 'Polar Angle (deg)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            magnitude = oscBetween(t, 'cos', self.params[0], self.params[1], self.params[2])
            fieldZ = magnitude * sind(self.params[4])
            fieldX = magnitude * cosd(self.params[4]) * cosd(self.params[3])
            fieldY = magnitude * cosd(self.params[4]) * sind(self.params[3])
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)
            if self.stopped:
                return
            
    def setPlotCanvas(self, canvas):
        self.canvas = canvas


    def rotateXY(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Magniude (mT)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            theta = 2 * pi * self.params[0] * t
            fieldX = self.params[1] * cos(theta)
            fieldY = self.params[2] * sin(theta)
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(0)
            if self.stopped:
                return

    def rotateYZ(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Magniude (mT)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            theta = 2 * pi * self.params[0] * t
            fieldY = self.params[1] * cos(theta)
            fieldZ = self.params[2] * sin(theta)
            self.field.setX(0)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)
            if self.stopped:
                return

    def rotateXZ(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Magniude (mT)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            theta = 2 * pi * self.params[0] * t
            fieldX = self.params[1] * cos(theta)
            fieldZ = self.params[2] * sin(theta)
            self.field.setX(fieldX)
            self.field.setY(0)
            self.field.setZ(fieldZ)
            if self.stopped:
                return
    
    def fromCSV(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, "data", "waveform.csv")

        df = pd.read_csv(csv_path)

        num_rows = len(df)

        for i in range(num_rows):
            x1 = df['X1_val'][i]
            x2 = df['X2_val'][i]
            y1 = df['Y1_val'][i]
            y2 = df['Y2_val'][i]
            z1 = df['Z1_val'][i]
            z2 = df['Z2_val'][i]

            self.field.dac.s826_aoPin(5, x1 / 4.433)  # X1
            self.field.dac.s826_aoPin(1, x2 / 5.024)  # X2
            self.field.dac.s826_aoPin(2, y1 / 5.224)  # Y1
            self.field.dac.s826_aoPin(6, y2 / 5.224)  # Y2
            self.field.dac.s826_aoPin(3, z1 / 4.879)  # Z1
            self.field.dac.s826_aoPin(7, z2 / 5.000)  # Z2

            x = x1 + x2
            y = y1 + y2
            z = z1 + z2
            self.field.x = x
            self.field.y = y
            self.field.z = z

         
            if i < num_rows - 1:
                dt = df['t'][i+1] - df['t'][i]
                time.sleep(max(0, dt)) 

            if self.stopped:
                print("✅ fromCSV thread stopped.")
                returnI

        print("✅ fromCSV completed")

    def formulaControlledField(self):
        import math
        from math import pi, sin, cos

        freq = 1
        start_time = time.time()

        while True:
            t = time.time() - start_time


            x = sin(pi*freq*t)
            # x = 0
            # y = 3 * cos(2 * pi * freq * t + pi / 2)
            y = 0
            # z = sin(2 * pi * freq * t) + cos(2 * pi * freq * t)
            z = 0
            x1 = x / 2
            x2 = x / 2
            y1 = y / 2
            y2 = y / 2
            z1 = z / 2
            z2 = z / 2

            self.field.dac.s826_aoPin(5, x1 / 4.433)  # X1
            self.field.dac.s826_aoPin(1, x2 / 5.024)  # X2
            self.field.dac.s826_aoPin(2, y1 / 5.224)  # Y1
            self.field.dac.s826_aoPin(6, y2 / 5.224)  # Y2
            self.field.dac.s826_aoPin(3, z1 / 4.879)  # Z1
            self.field.dac.s826_aoPin(7, z2 / 5.000)  # Z2

            self.field.x = x
            self.field.y = y
            self.field.z = z

  

            time.sleep(1 / 200)

            if self.stopped:
                print("✅ Formula controlled field stopped.")
                return
    
    def crawler_walking(self):
        #=============================
        # reference params
        # 0 'Bmax (mT)'
        # 1 'Frequency (Hz)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            bmax = self.params[0]
            freq = self.params[1]
            max2 = self.params[2]
            b_0 = (t % (1/freq)) * freq * bmax
            theta = pi + (t % (1/freq)) * freq * pi/4
            theta2 = 2 * pi * self.params[0] * t
            fieldX = b_0 * cos(theta)
            fieldY = b_0 * max2 * sin(theta)
            # fieldY = b_0 * sin(theta)
            field2 = bmax * sin(theta2)
            # self.field.setX(-max2)
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(0)
            if self.stopped:
                return
    
    def xy_angle(self):
        #=============================
        # reference params
        # 0 'Bmax (mT)'
        # 1 'Frequency (Hz)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            magnitude = self.params[0]
            angle = self.params[1]
            fieldX = magnitude * cosd(angle)
            fieldY = magnitude * sind(angle)
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(0)
            if self.stopped:
                return
        