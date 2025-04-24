from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from vision import CameraThread  

class CameraWindow(QWidget):
    def __init__(self, field_manager):
        super().__init__()
        self.setWindowTitle("Camera Window")
        self.resize(1600, 900)

        self.field = field_manager

    
        self.main_layout = QVBoxLayout(self)

        self.cameras = []
        self.canvases = []
        self.figures = []

        for i in range(3):
          
            row_layout = QHBoxLayout()

            label = QLabel(self)
            # label.setFixedSize(1536, 2048)
            label.setScaledContents(True)  
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  
            row_layout.addWidget(label)

            fig = plt.figure(figsize=(6, 3))
            canvas = FigureCanvas(fig)
            canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            row_layout.addWidget(canvas)

            self.main_layout.addLayout(row_layout)

            self.cameras.append(label)
            self.canvases.append(canvas)
            self.figures.append(fig)

        self.setLayout(self.main_layout)

        try:
            self.camThread1 = CameraThread(camera_index=0)
            self.camThread2 = CameraThread(camera_index=1)
            self.camThread3 = CameraThread(camera_index=2)

            self.camThread1.frame_ready.connect(lambda frame: self.display_frame(self.cameras[0], frame))
            self.camThread2.frame_ready.connect(lambda frame: self.display_frame(self.cameras[1], frame))
            self.camThread3.frame_ready.connect(lambda frame: self.display_frame(self.cameras[2], frame))

            self.camThread1.start()
            self.camThread2.start()
            self.camThread3.start()
        
        except Exception as e:
            print(f"Initializtion failed {e}")


        self.timer = QTimer()
        self.timer.timeout.connect(self.updateAllPlots)
        self.timer.start(200) 

    def display_frame(self, label, frame):
     
        if frame is None or frame.size == 0:
            return
        height, width, channel = frame.shape
        bytesPerLine = channel * width
        qtImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_BGR888)
        # label.setPixmap(QPixmap.fromImage(qtImg))
        pixmap = QPixmap.fromImage(qtImg).scaled(
            label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        label.setPixmap(pixmap)
        label.repaint()

    def updateAllPlots(self):
        x = self.field.x
        y = self.field.y
        z = self.field.z
        vec_norm = np.linalg.norm([x, y, z])
        radius = vec_norm + 5 if vec_norm > 0 else 15

        u, v = np.mgrid[0:2 * np.pi:30j, 0:np.pi:15j]
        sx = radius * np.cos(u) * np.sin(v)
        sy = radius * np.sin(u) * np.sin(v)
        sz = radius * np.cos(v)


        projections = [
            ("XZ", lambda x, y, z: (x, z)),
            ("XY", lambda x, y, z: (x, y)),
            ("YZ", lambda x, y, z: (y, z))
        ]

        for fig, canvas, (title, project_func) in zip(self.figures, self.canvases, projections):
            fig.clf()

            ax3d = fig.add_axes([0.05, 0.1, 0.4, 0.8], projection='3d')  # 3D 
            ax2d = fig.add_axes([0.55, 0.1, 0.4, 0.8])                   # 2D 

    
            ax3d.plot_surface(sx, sy, sz, color='white', alpha=0.2, edgecolor='none')
            ax3d.quiver(0, 0, 0, x, y, z, color='r', linewidth=2)
            ax3d.quiver(0, 0, 0, radius, 0, 0, color='b', linewidth=1, arrow_length_ratio=0.05)
            ax3d.quiver(0, 0, 0, 0, radius, 0, color='g', linewidth=1, arrow_length_ratio=0.05)
            ax3d.quiver(0, 0, 0, 0, 0, radius, color='k', linewidth=1, arrow_length_ratio=0.05)
            ax3d.text(radius, 0, 0, 'X', color='b')
            ax3d.text(0, radius, 0, 'Y', color='g')
            ax3d.text(0, 0, radius, 'Z', color='k')
            ax3d.set_xlim([-radius, radius])
            ax3d.set_ylim([-radius, radius])
            ax3d.set_zlim([-radius, radius])
            ax3d.set_title("XYZ")
            ax3d.axis('off')

            # 2D 投影图（使用指定投影）
            u2d, v2d = project_func(x, y, z)
            ax2d.add_patch(plt.Circle((0, 0), radius, color='r', fill=False))
            ax2d.arrow(0, 0, u2d, v2d, head_width=0.5, head_length=0.5, fc='r', ec='r')
            ax2d.set_xlim([-radius * 1.8, radius * 1.8])
            ax2d.set_ylim([-radius * 1.8, radius * 1.8])
            ax2d.set_aspect('equal')
            ax2d.set_title(title)
            ax2d.axis('off')

            canvas.draw()

    def closeEvent(self, event):
        try:
            self.camThread1.stop()
            self.camThread2.stop()
            self.camThread3.stop()
            self.camThread1.wait()
            self.camThread2.wait()
            self.camThread3.wait()
        except:
            pass
        event.accept()
