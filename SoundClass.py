import pygame
import pygame.midi
class MidiFeedback:
    def __init__(self,acc_x, acc_y, acc_z, acc_r, acc_phi, acc_theta, vel_x, vel_y, vel_z,
                 vel_r, vel_phi, vel_theta,instr_choice, mov_map_x, mov_map_y, mov_map_z, sound_map_x,
                 sound_map_y, sound_map_z):
        pygame.init()
        pygame.midi.init()
        pygame.mixer.init()
        device_id = None
        self.x_to_play,self.y_to_play, self.z_to_play = [],[],[]
        self.mov_map_x = mov_map_x
        self.mov_map_y = mov_map_y
        self.mov_map_z = mov_map_z
        self.acc_x = acc_x
        self.acc_y = acc_y
        self.acc_z = acc_z
        self.acc_r = acc_r
        self.acc_phi = acc_phi
        self.acc_theta = acc_theta
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.vel_z = vel_z
        self.vel_r = vel_r
        self.vel_phi = vel_phi
        self.vel_theta = vel_theta
        self.data_x = 0
        self.data_y = 0
        self.data_z = 0
        self.sound_map_x = sound_map_x
        self.sound_map_y = sound_map_y
        self.sound_map_z = sound_map_z
        self.pan_assignment = 0
        self.amplitude_assignment = 0
        self.frequency_assignment = 0
        self.instr_choice = instr_choice


        self.ratio_x = 0
        self.ratio_y = 0
        self.ratio_z = 0
        self.increment = 5 #how many samples are we skipping. NEEDS TO BE LOOKED AT
        self.i = 0 #this is a counter for the playback
        self.j = 0 #this is a counter for the control of note frequency
        self.audiorate = [] #used to moderate audio rate
        outpath = ("Folder")



        self.audioticks = pygame.time.get_ticks()
        if device_id is None:
            port = pygame.midi.get_default_output_id()
        else:
            port = device_id
            print ("using output_id :%s:" % port)
        self.midi_out = pygame.midi.Output(port, 0)
        self.initialising()

    def Instrument_choice(self):
        if (self.instr_choice == 'Saxophone'):
            self.instrument1 = 67
        elif(self.instr_choice == 'Violin'):
            self.instrument1 = 41
        elif(self.instr_choice == 'Piano'):
            self.instrument1 = 4
        else:
            print("Instrument not set")
    def MovMappingAction3(self):
        try:
            if(self.mov_map_x =='Velocity_x'):
                self.data_x = self.vel_x
            elif(self.mov_map_x =='Velocity_y'):
                self.data_x = self.vel_y
            elif(self.mov_map_x =='Velocity_z'):
                self.data_x = self.vel_z
            elif(self.mov_map_x =='Velocity_r'):
                self.data_x = self.vel_r
            elif(self.mov_map_x =='Velocity_phi'):
                self.data_x = self.vel_phi
            elif(self.mov_map_x =='Velocity_theta'):
                self.data_x = self.vel_theta
            elif(self.mov_map_x =='Acceleration_x'):
                self.data_x = self.acc_x
            elif(self.mov_map_x =='Acceleration_y'):
                self.data_x = self.acc_y
            elif(self.mov_map_x =='Acceleration_z'):
                self.data_x = self.acc_z
            elif(self.mov_map_x =='Acceleration_r'):
                self.data_x = self.acc_r
            elif(self.mov_map_x =='Acceleration_phi'):
                self.data_x = self.acc_phi
            elif(self.mov_map_x =='Acceleration_theta'):
                self.data_x = self.acc_theta
            else:
                print('MappingAction3 movement selector error')

        except:
            print('MappingAction3 error')

    def MovMappingAction5(self):
        try:
            if(self.mov_map_y =='Velocity_x'):
                self.data_y = self.vel_x
            elif(self.mov_map_y =='Velocity_y'):
                self.data_y = self.vel_y
            elif(self.mov_map_y =='Velocity_z'):
                self.data_y = self.vel_z
            elif(self.mov_map_y =='Velocity_r'):
                self.data_y = self.vel_r
            elif(self.mov_map_y =='Velocity_phi'):
                self.data_y = self.vel_phi
            elif(self.mov_map_y =='Velocity_theta'):
                self.data_y = self.vel_theta
            elif(self.mov_map_y =='Acceleration_x'):
                self.data_y = self.acc_x
            elif(self.mov_map_y =='Acceleration_y'):
                self.data_y = self.acc_y
            elif(self.mov_map_y =='Acceleration_z'):
                self.data_y = self.acc_z
            elif(self.mov_map_y =='Acceleration_r'):
                self.data_y = self.acc_r
            elif(self.mov_map_y =='Acceleration_phi'):
                self.data_y = self.acc_phi
            elif(self.mov_map_y =='Acceleration_theta'):
                self.data_y = self.acc_theta
            else:
                print('MappingAction5 movement selector error')

        except:
            print('MappingAction5 error')

    def MovMappingAction7(self):
        try:
            if(self.mov_map_z =='Velocity_x'):
                self.data_z = self.vel_x
            elif(self.mov_map_z =='Velocity_y'):
                self.data_z = self.vel_y
            elif(self.mov_map_z =='Velocity_z'):
                self.data_z = self.vel_z
            elif(self.mov_map_z =='Velocity_r'):
                self.data_z = self.vel_r
            elif(self.mov_map_z =='Velocity_phi'):
                self.data_z = self.vel_phi
            elif(self.mov_map_z =='Velocity_theta'):
                self.data_z = self.vel_theta
            elif(self.mov_map_z =='Acceleration_x'):
                self.data_z = self.acc_x
            elif(self.mov_map_z =='Acceleration_y'):
                self.data_z = self.acc_y
            elif(self.mov_map_z =='Acceleration_z'):
                self.data_z = self.acc_z
            elif(self.mov_map_z =='Acceleration_r'):
                self.data_z = self.acc_r
            elif(self.mov_map_z =='Acceleration_phi'):
                self.data_z = self.acc_phi
            elif(self.mov_map_z=='Acceleration_theta'):
                self.data_z = self.acc_theta
            else:
                print('MappingAction7 movement selector error')

        except:
            print('MappingAction7 error')

    def SoundMappingAction3(self):
        try:

            if (self.sound_map_x == 'Frequency'):
                self.frequency_assignment = self.x_to_play
            elif(self.sound_map_x =='Spatial'):
                self.pan_assignment = self.x_to_play
            elif(self.sound_map_x =='Amplitude'):
                self.amplitude_assignment = self.x_to_play
            else:
                print('SoundMappingAction3 sound selector error')

        except:
            print('SoundMappingAction3 error')

    def SoundMappingAction5(self):
        try:

            if (self.sound_map_y == 'Frequency'):
                self.frequency_assignment = self.y_to_play
            elif(self.sound_map_y =='Spatial'):
                self.pan_assignment = self.y_to_play
            elif(self.sound_map_y =='Amplitude'):
                self.amplitude_assignment = self.y_to_play
            else:
                print('SoundMappingAction5 sound selector error')

        except:
            print('SoundMappingAction5 error')

    def SoundMappingAction7(self):
        try:

            if (self.sound_map_z == 'Frequency'):
                self.frequency_assignment = self.z_to_play
            elif(self.sound_map_z =='Spatial'):
                self.pan_assignment = self.z_to_play
            elif(self.sound_map_z =='Amplitude'):
                self.amplitude_assignment = self.z_to_play
            else:
                print('SoundMappingAction7 sound selector error')

        except:
            print('SoundMappingAction7 error')

    def initialising(self):
        print("initialising")
        try:
            for i in range(pygame.midi.get_count()):

                r = pygame.midi.get_device_info(i)
                (interf, name, input, output, opened) = r
                in_out = ""
                if input:
                    in_out = "(input)"
                if output:
                    in_out = "(output)"
                print("%2i: interface :%s:, name :%s:, opened :%s:  %s" %(i, interf, name, opened, in_out))

            self.Instrument_choice()
            self.MovMappingAction3()
            self.MovMappingAction5()
            self.MovMappingAction7()
            print("Movement is mapped")
            self.midi_out.set_instrument(self.instrument1)

            self.ratio_x = (max(self.data_x) - min(self.data_x))/127
            self.ratio_y = (max(self.data_y) - min(self.data_y))/127
            self.ratio_z = (max(self.data_z) - min(self.data_z))/127

            self.x_to_play = ((self.data_x) - min(self.data_x))/self.ratio_x
            self.y_to_play = ((self.data_y) - min(self.data_y))/self.ratio_y
            self.z_to_play = ((self.data_z) - min(self.data_z))/self.ratio_z
            print("data converted")

            self.audiorate.append(pygame.time.get_ticks()) #used to moderate audio rate
            self.SoundMappingAction3()
            self.SoundMappingAction5()
            self.SoundMappingAction7()
            print("Sound is mapped")

            #self.midi_out.write_short(0xb0, 0x0A, int(self.pan_assignment[self.i]))#this is the pan control, can only be between 0-127
            #self.midi_out.write_short(0xb0, 0x07, int(self.amplitude_assignment[self.i]))#this is the amplitude control
            #self.midi_out.note_on(int(self.frequency_assignment[self.i]), 127) #this is the pitch control
            try:
                self.midi_out.write_short(0xb0, 0x0A, int(self.pan_assignment[self.i]))#this is the pan control, can only be between 0-127
                self.midi_out.write_short(0xb0, 0x07, int(self.amplitude_assignment[self.i]))#this is the amplitude control
                self.midi_out.note_on(int(self.frequency_assignment[self.i]), 127) #this is the pitch control
            except:
                print("couldn't assign")
            self.i += self.increment
        except:
            print("Initialising error")


    def audioFeedback(self):

        #Midi control

        ### For the pan control: Due to the orientation of the NGIMU, the maximum value is to the left of the user,
        ### therefore for a right handed user, that reaches right, must have a pan value of 0, to hear the audio from
        ### the right speaker.
        if(int(self.pan_assignment[self.i] == 63)):
            self.midi_out.write_short(0xb0, 0x0A, 63)#this is the pan control, can only be between 0-127
        elif(int(self.pan_assignment[self.i] < 63)):
            self.midi_out.write_short(0xb0, 0x0A, 127)#this is the pan control, can only be between 0-127
        elif(int(self.pan_assignment[self.i] > 63)):
            self.midi_out.write_short(0xb0, 0x0A, 0)
        else:
            print("Pan Incorrectly Assigned")

        #self.midi_out.write_short(0xb0, 0x0A, int(self.pan_assignment[self.i]))#this is the pan control, can only be between 0-127
        self.midi_out.write_short(0xb0, 0x07, int(self.amplitude_assignment[self.i]))#this is the amplitude control
        self.midi_out.note_on(int(self.frequency_assignment[self.i]), 127) #this is the pitch control
        self.midi_out.note_off(int(self.frequency_assignment[self.i-self.increment]))#turns off the previous note sound
        #Midi control
      #  self.j += 1
      #  self.audiorate.append(self.audioticks)

       # audio_time_diff = int(self.audiorate[self.j] - self.audiorate[(self.j)-1])
       # print("SoundClass delay:",abs(audio_time_diff))
       # audio_delay = abs(80 - audio_time_diff)
        #print(audio_delay)
       # pygame.time.delay(audio_delay)
       # print("AD:",audio_delay)
        #sets the duration of the note along with plt.pause()
        if self.i < (len(self.data_x)-self.increment):
            self.i += self.increment
        else:
            self.i = 0 #reset counter for the saving of images

#midi setup function
