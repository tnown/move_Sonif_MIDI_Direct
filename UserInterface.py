import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from pyqtgraph.dockarea import *
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import csv
from collections import deque
from IntegratedGUI.IntegratedGuiV1.MovementParameters import MovementParameters
from IntegratedGUI.IntegratedGuiV1.NoiseThreshold import NoiseThreshold
from IntegratedGUI.SoundClass import MidiFeedback #here's a problem with this one
import time
import pygame
import pygame.midi
import qdarkgraystyle



class MyWindow(QtGui.QWidget):

    def __init__(self, parent = None):
        super(MyWindow, self).__init__(parent)
        self.sampled_frequency, self.noise_thr, self.audio_counter, self.rate_counter = 0,0,0,0

        #sampled frequency is needed throughout
        #noise threshold is an arbirtrary value calculated by the noise class
        #audio counter is required to cycle through extracted data to sonify
        #
       # self.noise_thr = 0
       # self.audio_counter = 0

       # self.rate_counter = 0
        self.app = QtGui.QApplication([])
        self.win = QtGui.QMainWindow()
        self.app.setStyleSheet(qdarkgraystyle.load_stylesheet()) #sets the theme
        area = DockArea()
        self.win.setCentralWidget(area)
        self.win.resize(1000,320)
        self.win.setWindowTitle('User Interface')
        #set the main window
        # set the individual widget sizes and layout
        d1 = Dock("Data Management", size=(1000,20))
        d2 = Dock("Graph 1", size=(600,50))
        d3 = Dock("Settings 1", size=(400,50))
        d4 = Dock("Graph 2", size=(600,50))
        d5 = Dock("Settings 2", size=(400,50))
        d6 = Dock("Graph 3", size=(600,50))
        d7 = Dock("Settings 3", size=(400,50))
        d10 = Dock("Play", size=(1000,20))
        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom',d1)
        area.addDock(d3, 'right', d2)
        area.addDock(d4, 'bottom',d2)
        area.addDock(d5, 'bottom', d3)
        area.addDock(d6, 'bottom', d4)
        area.addDock(d7, 'bottom', d5)
        area.addDock(d10,'bottom')
        # set the individual widget sizes and layout
        #Create title widget - which will have instrument control and data management
        self.w1 = pg.LayoutWidget()
        self.w1.addWidget(QtGui.QLabel('Select Instrument'), row = 0, col = 0)
        self.w1.Instrument_selector = QtGui.QComboBox()
        self.w1.Instrument_selector.addItems(['Saxophone', 'Piano', 'Violin'])
        self.w1.addWidget(self.w1.Instrument_selector, row = 0, col = 1)
         #w1.addWidget(QtGui.QLineEdit())
        d1.addWidget(self.w1)
    # create plot windows
        self.initArrays()
        self.askUser()
        self.NoiseCalc()
        self.dataLoad()
        self.xd = np.linspace(0, (1/self.sampled_frequency)*len(self.raw_x), len(self.raw_x))

        self.PlotWindow2 = pg.PlotWidget()
        self.PlotWindow4 = pg.PlotWidget()
        self.PlotWindow6 = pg.PlotWidget()
        d2.addWidget(self.PlotWindow2)
        d4.addWidget(self.PlotWindow4)
        d6.addWidget(self.PlotWindow6)
        self.plotline_w2 = self.PlotWindow2.plot()
        self.plotline_w2.setPen((200,200,100))
        self.plotline_w4 = self.PlotWindow4.plot()
        self.plotline_w4.setPen((200,200,100))
        self.plotline_w6 = self.PlotWindow6.plot()
        self.plotline_w6.setPen((200,200,100))
        self.t = 0
        self.n = 0
        self.deque2 = deque(np.zeros(1000), maxlen=1000)
        self.deque4 = deque(np.zeros(1000), maxlen=1000)
        self.deque6 = deque(np.zeros(1000), maxlen=1000)

    # create plot windows
    # create settings windows
        #self.w3 = self.SettingsWidget()
        self.w3 = pg.LayoutWidget()
        self.w3.Movement_selector = QtGui.QComboBox(self)
        self.w3.Movement_selector.addItems(['Acceleration_x','Acceleration_y','Acceleration_z',
                                            'Acceleration_r','Acceleration_theta','Acceleration_phi',
                                            'Velocity_x', 'Velocity_y', 'Velocity_z',
                                            'Velocity_r', 'Velocity_phi', 'Velocity_theta'])
        self.w3.Sound_selector = QtGui.QComboBox(self)
        self.w3.Sound_selector.addItems([ 'Amplitude', 'Spatial', 'Frequency'])
        self.w3.addWidget(self.w3.Movement_selector, row = 0, col = 0)
        self.w3.addWidget(self.w3.Sound_selector, row = 1, col = 0)
        #self.w3.Submit = QtGui.QPushButton('Submit', self)
        #self.w3.Submit.clicked.connect(self.PrintingAction3)
        #self.w3.addWidget(self.w3.Submit, row=2, col=0)

        self.w5 = pg.LayoutWidget()
        self.w5.Movement_selector = QtGui.QComboBox(self)
        self.w5.Movement_selector.addItems(['Acceleration_x','Acceleration_y','Acceleration_z',
                                            'Acceleration_r','Acceleration_theta','Acceleration_phi',
                                            'Velocity_x', 'Velocity_y', 'Velocity_z',
                                            'Velocity_r','Velocity_phi', 'Velocity_theta'])
        self.w5.Sound_selector = QtGui.QComboBox(self)
        self.w5.Sound_selector.addItems(['Spatial','Amplitude','Frequency'])
        self.w5.addWidget(self.w5.Movement_selector, row = 0, col = 0)
        self.w5.addWidget(self.w5.Sound_selector, row = 1, col = 0)
        #self.w5.Submit = QtGui.QPushButton('Submit', self)
        #self.w5.Submit.clicked.connect(self.PrintingAction5)
        #self.w5.addWidget(self.w5.Submit, row=2, col=0)

        self.w7 = pg.LayoutWidget()
        self.w7.Movement_selector = QtGui.QComboBox(self)
        self.w7.Movement_selector.addItems(['Acceleration_x','Acceleration_y','Acceleration_z',
                                            'Acceleration_r','Acceleration_theta','Acceleration_phi',
                                            'Velocity_x', 'Velocity_y', 'Velocity_z',
                                            'Velocity_r', 'Velocity_phi', 'Velocity_theta'])
        self.w7.Sound_selector = QtGui.QComboBox(self)
        self.w7.Sound_selector.addItems(['Frequency', 'Amplitude', 'Spatial'])
        self.w7.addWidget(self.w7.Movement_selector, row = 0, col = 0)
        self.w7.addWidget(self.w7.Sound_selector, row = 1, col = 0)
        #self.w7.Submit = QtGui.QPushButton('Submit', self)
        #self.w7.Submit.clicked.connect(self.PrintingAction7)
        #self.w7.addWidget(self.w7.Submit, row=2, col=0)


        self.w10 = pg.LayoutWidget()
        self.w10.Play = QtGui.QPushButton('Play',self)
        self.w10.Play.clicked.connect(self.playData)
        self.w10.addWidget(self.w10.Play, row = 0, col = 0)

        d3.addWidget(self.w3)
        d5.addWidget(self.w5)
        d7.addWidget(self.w7)
        d10.addWidget(self.w10)
        self.win.show()



        #self.rate.append(pygame.time.get_ticks())
    #create settings window

    # def SettingsWidget(self):
    #     self.Settings = pg.LayoutWidget()
    #     self.Settings.Movement_selector = QtGui.QComboBox(self)
    #     self.Settings.Movement_selector.addItems(['Acceleration', 'Velocity', 'Position'])
    #     self.Settings.Sound_selector = QtGui.QComboBox(self)
    #     self.Settings.Sound_selector.addItems(['Frequency', 'Amplitude', 'Spatial'])
    #     self.Settings.addWidget(self.Settings.Movement_selector, row = 0, col = 0)
    #     self.Settings.addWidget(self.Settings.Sound_selector, row = 1, col = 0)
    #     return self.Settings

    def initArrays(self):
        self.noise_raw_x, self.noise_raw_y, self.noise_raw_z = [],[],[]
        self.raw_x, self.raw_y, self.raw_z = [],[],[]
        self.acc_x, self.acc_y, self.acc_z = [],[],[]
        self.acc_r, self.acc_phi, self.acc_theta = [],[],[]
        self.vel_x, self.vel_y, self.vel_z = [],[],[]
        self.vel_r, self.vel_phi, self.vel_theta = [],[],[]
        self.rate = [] #used to moderate audio rate


    def askUser(self): #Ask user for sampling frequency
        print("What is the sample frequency?")
        self.sampled_frequency = int(input())
        return self.sampled_frequency

    def NoiseCalc(self): #Function for calculating the noise threshold
        Tk().withdraw()
        filename = askopenfilename() #show an \"Open\" dialog box and return the path to the selected file
        with open(filename) as Block_csv:
            Block_reader = csv.reader(Block_csv, delimiter=',')
            first_line = Block_csv.readline() #remove first line
            for row in Block_reader:
             #row[0] is the time column
                self.noise_raw_x.append(float(row[1])*9.81)
                self.noise_raw_y.append(float(row[2])*9.81)
                self.noise_raw_z.append(float(row[3])*9.81)
        noise_thr = NoiseThreshold(self.noise_raw_x, self.noise_raw_y, self.noise_raw_z, self.sampled_frequency)
        self.noise_thr = noise_thr.getThreshold()
        print("My noise threshold is set to", self.noise_thr)
        return self.noise_thr

###### This will be used for real time######
    # def dataLoad(self):
    #     Tk().withdraw()
    #     self.filename = askopenfilename() #show an \"Open\" dialog box and return the path to the selected file
    #     with open(self.filename) as Block_csv:
    #         self.Block_reader = csv.reader(Block_csv, delimiter=',')
    #         self.first_line = Block_csv.readline() #remove first line
    #         MovePara = MovementParameters(self.raw_x,self.raw_y, self.raw_z, self.sampled_frequency, self.noise_thr )
    #         for self.row in self.Block_reader:
    #          #row[0] is the time column
    #             self.raw_x.append(float(self.row[1])*9.81)
    #             self.raw_y.append(float(self.row[2])*9.81)
    #             self.raw_z.append(float(self.row[3])*9.81)
    #             self.t = QtCore.QTimer()
    #             self.t.timeout.connect(self.updateData)
    #             self.t.start(10)
##### This will be used for real time######

    def dataLoad(self):
        Tk().withdraw()
        filename = askopenfilename() #show an \"Open\" dialog box and return the path to the selected file
        with open(filename) as Block_csv:
            Block_reader = csv.reader(Block_csv, delimiter=',')
            first_line = Block_csv.readline() #remove first line
            for row in Block_reader:
        #row[0] is the time column
                self.raw_x.append(float(row[1])*9.81)
                self.raw_y.append(float(row[2])*9.81)
                self.raw_z.append(float(row[3])*9.81)

        MovePara = MovementParameters(self.raw_x,self.raw_y, self.raw_z, self.sampled_frequency, self.noise_thr)
        self.acc_x, self.acc_y, self.acc_z,self.acc_r, self.acc_phi, self.acc_theta,self.vel_x, self.vel_y, self.vel_z, self.vel_r, self.vel_theta, self.vel_phi = MovePara.getMotionPara()
        print("Data has been loaded")

    def playData(self):
        try:
            print("playData")
            #self.sound = MidiFeedback(self.data_x, self.data_y, self.data_z, self.map_x, self.map_y, self.map_z)
            self.sound = MidiFeedback(self.acc_x, self.acc_y, self.acc_z,
                                      self.acc_r, self.acc_phi, self.acc_theta,
                                      self.vel_x, self.vel_y, self.vel_z,
                                      self.vel_r, self.vel_phi, self.vel_theta,
                                      self.w1.Instrument_selector.currentText(),
                                      self.w3.Movement_selector.currentText(),
                                      self.w5.Movement_selector.currentText(),
                                      self.w7.Movement_selector.currentText(),
                                      self.w3.Sound_selector.currentText(),
                                      self.w5.Sound_selector.currentText(),
                                      self.w7.Sound_selector.currentText())
            self.rate.append(pygame.time.get_ticks())
            self.t = QtCore.QTimer()
            print("updateData")
            self.t.timeout.connect(self.updateData)
       # sound.calculateMidiNote()
            self.t.start(1)
        except:
            print("playData failed")


    def updateData(self):
        self.n += 1
        self.audio_counter += 1

        self.rate.append(pygame.time.get_ticks())
        time_diff = int(self.rate[self.n] - self.rate[(self.n)-1])

        delay = int((1/(self.sampled_frequency/1000))) - time_diff

        if (delay > 0):
            pygame.time.delay(delay)
            self.rate[self.n] = pygame.time.get_ticks()

        #print("User Interface delay:", time_diff + delay)

        self.deque2.append(self.sound.data_x[self.n])
        self.deque4.append(self.sound.data_y[self.n])
        self.deque6.append(self.sound.data_z[self.n])

        self.plotline_w2.setData(self.deque2)
        self.plotline_w2.setPos(self.n, 0)
        self.plotline_w4.setData(self.deque4)
        self.plotline_w4.setPos(self.n, 0)
        self.plotline_w6.setData(self.deque6)
        self.plotline_w6.setPos(self.n, 0)

        if (self.audio_counter == 5):
            self.sound.audioFeedback()
            self.audio_counter = 0

        if (self.n == (len(self.sound.data_x)-1)):
            print("UpdateData finished")
            self.n = 0
            input("Press Enter to continue")
            #self.w10.Play.clicked.connect(self.playData)

        #print(self.n)
        #print(len(self.sound.data_x))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = MyWindow()
    sys.exit(app.exec_())



