"""
The following code is used to convert a .tsv file into sound, the z axis,
represents the causal/caudal direction, and controls the sound pitch,
the y axis, represents the anterior/posterior direction,
and controls the amplitude of the sound, the x axis represents
the medial/lateral direction, and controls the pan of the sound
between the left and right speaker.
The script also does the following:
- After initial sonification run, the plots are saved as images at every increment
- Those images are turned into videos
- During the initial run of sonification, the audio from the speakers is recorded
through Audacity
- The sound recorded is saved to a specific file, which is then taken and attached to
to the created video
- The algorithm for determining pitch, volume, and pan is general
- The rate of midi notes turning on and off is set to 0.1s to maintain
a constant continuous sound
Author: Tom Nown
Created on: 05/07/2019
"""

import csv
import numpy as np
import pygame
import pygame.midi
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import os
import sys
import time
from os import path
import cv2
import glob
from moviepy.editor import *
import datetime
from midiutil.MidiFile import MIDIFile
from tkinter import Tk
from tkinter.filedialog import askopenfilename

#Audacity setup section
if( sys.platform  == 'win32' ):
    toname = '\\\\.\\pipe\\ToSrvPipe'
    fromname = '\\\\.\\pipe\\FromSrvPipe'
    EOL = '\r\n\0'
else:
    print( "recording-test.py, running on linux or mac" )
    toname = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
    fromname = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
    EOL = '\n'

print( "Write to  \"" + toname +"\"" )
if not os.path.exists( toname ) :
   print( " ..does not exist.  Ensure Audacity is running with mod-script-pipe." )
   sys.exit();

print( "Read from \"" + fromname +"\"")
if not os.path.exists( fromname ) :
   print( " ..does not exist.  Ensure Audacity is running with mod-script-pipe." )
   sys.exit();

print( "-- Both pipes exist.  Good." )

tofile = open(toname, 'wt+')
print("-- File to write to has been opened" )
fromfile = open(fromname, 'rt')
print( "-- File to read from has now been opened too\r\n" )

def sendCommand( command ) :
    print( "Send: >>> "+command )
    tofile.write( command + EOL )
    tofile.flush()

def getResponse() :
    result = ''
    line = ''
    while line != '\n' :
        result += line
        line = fromfile.readline()
	#print(" I read line:["+line+"]")
    return result

def do( command ) :
    sendCommand( command )
    response = getResponse()
    print( "Rcvd: <<< " + response )
    return response

def exportIt():
    do("Select: Track=1")
    do("Export: Filename: 'C:\\Users\\CDT167\\PycharmProjects\\Project\\SoundRecorded.wav' Mode=Selection Channels = 1.0")
#Audacity setup section

#midi setup function
def _print_device_info():
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r
        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print ("%2i: interface :%s:, name :%s:, opened :%s:  %s" %
               (i, interf, name, opened, in_out))
#midi setup function

pygame.init()
pygame.midi.init()
pygame.mixer.init()
_print_device_info()

device_id = None

if device_id is None:
    port = pygame.midi.get_default_output_id()
else:
    port = device_id
    print ("using output_id :%s:" % port)

#--------------------------------------------------------------------------
class BodyPart:
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
#importing code
    dx = 0.005
    x = []
    y = []
    z = []
    vel_x = []
    vel_y = []
    vel_z = []
    filt_vel_x = []
    filt_vel_y = []
    filt_vel_z = []
    acc_x = []
    acc_y = []
    acc_z = []
    filt_acc_x = []
    filt_acc_y = []
    filt_acc_z = []

    with open(filename) as Block_csv:
        Block_reader = csv.reader(Block_csv, delimiter='\t')
        first_line = Block_csv.readline()
            #importing code
        for row in Block_reader:
            x.append(float(row[0]))
            y.append(float(row[1]))
            z.append(float(row[2]))

    b, a = signal.butter(5, 0.05)
    zi = signal.lfilter_zi(b, a)
    filt_x, _ = signal.lfilter(b, a, x, zi=zi*x[0])
    filt_y, _ = signal.lfilter(b, a, y, zi=zi*y[0])
    filt_z, _ = signal.lfilter(b, a, z, zi=zi*z[0])
    data_length = len(x)
#differentiate with respect to time - Velocity
    vel_counter = [i for i in range(data_length-1)]
    for i in vel_counter:
        filt_vel_x.append(((filt_x[i+1]-filt_x[i])/dx))
        filt_vel_y.append(((filt_y[i+1]-filt_y[i])/dx))
        filt_vel_z.append(((filt_z[i+1]-filt_z[i])/dx))
#differentiate with respect to time - Velocity

#differentiate with respect to time - Acceleration
    acc_counter = [a for a in range(data_length-2)]
    for a in acc_counter:
        filt_acc_x.append(((filt_vel_x[a+1]-filt_vel_x[a])/dx))
        filt_acc_y.append(((filt_vel_y[a+1]-filt_vel_y[a])/dx))
        filt_acc_z.append(((filt_vel_z[a+1]-filt_vel_z[a])/dx))
#differentiate with respect to time - Acceleration
    t = np.linspace(0, data_length-1, data_length)
    t_vel = np.linspace(0, data_length-2, data_length-1)
    t_acc = np.linspace(0, data_length-3, data_length-2)

    value_range_x = max(filt_x) - min(filt_x)
    value_range_y = max(filt_y) - min(filt_y)
    value_range_z = max(filt_z) - min(filt_z)
    ratio_x = value_range_x/100
    ratio_y = value_range_y/100
    ratio_z = value_range_z/100

    def plotGraphs(self,t,data_x, data_y, data_z):
        plt.figure(1)
        circle = mpath.Path.unit_circle()
        top = plt.subplot(311)
        line1, = plt.plot(t, data_x, label='Third_Finger_x')
        plt.ylabel("x-axis")
        middle = plt.subplot(312)
        line2, = plt.plot(t, data_y, label='Third_Finger_y')
        plt.ylabel("y-axis")
        bottom = plt.subplot(313)
        line3, = plt.plot(t, data_z, label='Third_Finger_z')
        plt.ylabel("z-axis")
        plt.xlabel("Number of captured sample")
        plt.ion()
        plt.show()
        plt.draw()
        plt.pause(0.2)

ThirdFinger = BodyPart()
ThirdFinger.plotGraphs(ThirdFinger.t,ThirdFinger.filt_x, ThirdFinger.filt_y, ThirdFinger.filt_z)

#audio section
midi_out = pygame.midi.Output(port, 0)

x_to_play = ((ThirdFinger.filt_x) - min(ThirdFinger.filt_x))/ThirdFinger.ratio_x
y_to_play = ((ThirdFinger.filt_y) - min(ThirdFinger.filt_y))/ThirdFinger.ratio_y
z_to_play = ((ThirdFinger.filt_z) - min(ThirdFinger.filt_z))/ThirdFinger.ratio_z

audiorate = [] #used to moderate audio rate
audiorate.append(pygame.time.get_ticks()) #used to moderate audio rate
#audio section

#counters for the while loop
i = 0
j = 0
#counters for the while loop

circle = mpath.Path.unit_circle() #required for visual tracking

increment = 20
#instrument selection
instrument1 = 4
instrument2 = 64
#instrument selection

#needed for plotting marker on graphs
line12, = plt.plot(ThirdFinger.t[i],ThirdFinger.filt_x[i],'--r', marker = circle, markersize=5)
line22, = plt.plot(ThirdFinger.t[i],ThirdFinger.filt_y[i],'--r', marker = circle, markersize=5)
line32, = plt.plot(ThirdFinger.t[i],ThirdFinger.filt_z[i],'--r', marker = circle, markersize=5)
#needed for plotting marker on graphs




outpath = "Folder"
    #instruments can be found through https://jazz-soft.net/demo/GeneralMidi.html
try:
    midi_out.set_instrument(instrument1)
    do("Record2ndChoice:")
    while 1:
        #Midi control
        midi_out.write_short(0xb0, 0x0A, int(x_to_play[i]))
        #this is the pan control, can only be between 0-127
        midi_out.write_short(0xb0, 0x07, int(y_to_play[i]))
        #this is the amplitude control
        midi_out.note_on(int(z_to_play[i]), 127)
        midi_out.note_on(int(z_to_play[i] + 4), 127)
        midi_out.note_on(int(z_to_play[i] + 7), 127)
        #this is the pitch control
        #Midi control

        #this shows the marker going along the three axis
        plt.subplot(311)
        line12.remove()
        line12, = plt.plot(ThirdFinger.t[i],ThirdFinger.filt_x[i],'--r', marker = circle, markersize=5)
        plt.subplot(312)
        line22.remove()
        line22, = plt.plot(ThirdFinger.t[i],ThirdFinger.filt_y[i],'--r', marker = circle, markersize=5)
        plt.subplot(313)
        line32.remove()
        line32, = plt.plot(ThirdFinger.t[i],ThirdFinger.filt_z[i],'--r', marker = circle, markersize=5)
        plt.draw()
        plt.pause(0.001) # gives time for markers to update, smooths the music

        j += 1
        audiorate.append(pygame.time.get_ticks())
        time_diff = int(audiorate[j] - audiorate[j-1])
        delay = abs(100 - time_diff)
        pygame.time.delay(delay)
        audiorate[j] = pygame.time.get_ticks()

        #sets the duration of the note along with plt.pause()

        midi_out.note_off(int(z_to_play[i]))
        midi_out.note_off(int(z_to_play[i])+ 4)
        midi_out.note_off(int(z_to_play[i])+ 7)
        #turns off the note sound

        if i < (ThirdFinger.data_length-increment):
            i += increment
        else:
            i = 0 #reset counter for the saving of images
            do("PlayStop:")
            exportIt()
            break
    while 1:
        #goes through the plots again and saves images
        plt.subplot(311)
        line12.remove()
        line12, = plt.plot(ThirdFinger.t[i],ThirdFinger.filt_x[i],'--r', marker = circle, markersize=5)
        plt.subplot(312)
        line22.remove()
        line22, = plt.plot(ThirdFinger.t[i],ThirdFinger.filt_y[i],'--r', marker = circle, markersize=5)
        plt.subplot(313)
        line32.remove()
        line32, = plt.plot(ThirdFinger.t[i],ThirdFinger.filt_z[i],'--r', marker = circle, markersize=5)
        plt.draw()
        plt.pause(0.001) # gives time for markers to update, smooths the music
        plt.savefig(path.join(outpath,"dataname-{0}.png".format(int(i/20))))
        if i < (ThirdFinger.data_length-increment):
            i += increment
        else:
            i = 0
            break
        #goes through the plots again and saves images
finally:
#create video from saved images
    img_array = []
    for j in range(int(ThirdFinger.data_length/increment)):
        for filename in glob.glob('Folder\dataname-{0}.png'.format(j)):
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width,height)
            img_array.append(img)
            out = cv2.VideoWriter('project.avi',cv2.VideoWriter_fourcc(*'DIVX'), 10, size)
    for k in range(len(img_array)):
        out.write(img_array[k])
    out.release()
#create video from saved images

#attaching sound to video section
    audioclip = AudioFileClip("HarmonyRecorded.wav")
    videoclip = VideoFileClip("project.avi")
    videoclip2 = videoclip.set_audio(audioclip)
    videoclip2.write_videofile("ProjectWithSound.mp4", fps = 10, codec = 'mpeg4')
#attaching sound to video section

    print("quit")
    do("TrackClose:")
    del midi_out
    pygame.midi.quit()
    pygame.mixer.quit()
    pygame.quit()

