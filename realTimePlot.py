import matplotlib
import numpy as np
from PyQt5.QtCore import pyqtSlot
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class CustomFigCanvas(TimedAnimation, FigureCanvas):
    ''' A class that inherited matplotlib backend. used for plotting field value in real time. '''
    def __init__(self):
        self.addedDataX = []
        self.addedDataY = []
        self.addedDataZ = []
        self.ylimRange = [-14,14]
        self.isZoomed = False
        # print(matplotlib.__version__)

        # data
        self.numberOfSamplesStored = 200
        self.t = np.linspace(0, self.numberOfSamplesStored - 1, self.numberOfSamplesStored)
        self.x = (self.t * 0.0)
        self.y = (self.t * 0.0)
        self.z = (self.t * 0.0)
        # The window
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.fig.patch.set_facecolor((0.92, 0.92, 0.92))
        self.ax1 = self.fig.add_subplot(111)
        # self.ax1 settings
        self.ax1.set_ylabel('field XYZ')
        # line1 X
        self.line1 = Line2D([], [], color='blue')
        self.line1_tail = Line2D([], [], color='blue', linewidth=2)
        self.line1_head = Line2D([], [], color='blue', marker='o', markeredgecolor='blue')
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)
        # line1 Y
        self.line2 = Line2D([], [], color='green')
        self.line2_tail = Line2D([], [], color='green', linewidth=2)
        self.line2_head = Line2D([], [], color='green', marker='o', markeredgecolor='green')
        self.ax1.add_line(self.line2)
        self.ax1.add_line(self.line2_tail)
        self.ax1.add_line(self.line2_head)
        # line1 Z
        self.line3 = Line2D([], [], color='red')
        self.line3_tail = Line2D([], [], color='red', linewidth=2)
        self.line3_head = Line2D([], [], color='red', marker='o', markeredgecolor='red')
        self.ax1.add_line(self.line3)
        self.ax1.add_line(self.line3_tail)
        self.ax1.add_line(self.line3_head)
        #lim
        self.ax1.set_xlim(0, self.numberOfSamplesStored - 1)
        self.ax1.set_ylim(self.ylimRange[0], self.ylimRange[1])
        self.ax1.get_xaxis().set_visible(False)
        # init
        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval = 50, blit = True)

    # ========================================================
    # connected to signel callback signal
    # ========================================================
    def addDataX(self, value): self.addedDataX.append(value)
    def addDataY(self, value): self.addedDataY.append(value)
    def addDataZ(self, value): self.addedDataZ.append(value)

    def new_frame_seq(self):
        return iter(range(self.t.size))

    def _init_draw(self):
        lines = [self.line1, self.line1_tail, self.line1_head,self.line2, self.line2_tail, self.line2_head,self.line3, self.line3_tail, self.line3_head]
        for l in lines:
            l.set_data([], [])

    def zoom(self, value):
        if self.isZoomed:
            self.ax1.set_ylim(self.ylimRange[0],self.ylimRange[1])
        else:
            self.ax1.set_ylim(self.ylimRange[0]/2,self.ylimRange[1]/2)
        self.draw()
        self.isZoomed = not self.isZoomed

    def _draw_frame(self, frame):
        margin = 2
        
        # Process all added data points
        while len(self.addedDataX) > 0:
            self.x = np.roll(self.x, -1)
            self.y = np.roll(self.y, -1)
            self.z = np.roll(self.z, -1)
            self.x[-1] = self.addedDataX.pop(0)  # Pop from the front of the list
            self.y[-1] = self.addedDataY.pop(0)
            self.z[-1] = self.addedDataZ.pop(0)
        
        # Set the data for lines
        self.line1.set_data(self.t[:-margin], self.x[:-margin])
        self.line2.set_data(self.t[:-margin], self.y[:-margin])
        self.line3.set_data(self.t[:-margin], self.z[:-margin])

        # Update tails with the last 10 points + margin
        self.line1_tail.set_data(np.concatenate((self.t[-10:-1-margin], [self.t[-1-margin]])), np.concatenate((self.x[-10:-1-margin], [self.x[-1-margin]])))
        self.line2_tail.set_data(np.concatenate((self.t[-10:-1-margin], [self.t[-1-margin]])), np.concatenate((self.y[-10:-1-margin], [self.y[-1-margin]])))
        self.line3_tail.set_data(np.concatenate((self.t[-10:-1-margin], [self.t[-1-margin]])), np.concatenate((self.z[-10:-1-margin], [self.z[-1-margin]])))

        # Set heads (last point with margin)
        self.line1_head.set_data([self.t[-1-margin]], [self.x[-1-margin]])
        self.line2_head.set_data([self.t[-1-margin]], [self.y[-1-margin]])
        self.line3_head.set_data([self.t[-1-margin]], [self.z[-1-margin]])

        # Return all updated lines for blitting
        return [self.line1, self.line1_tail, self.line1_head,
                self.line2, self.line2_tail, self.line2_head,
                self.line3, self.line3_tail, self.line3_head]
