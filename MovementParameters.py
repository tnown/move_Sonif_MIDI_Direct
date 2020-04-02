import numpy as np
import pandas as pd
from scipy import signal
from scipy.integrate import trapz

class MovementParameters:
    def __init__(self,raw_x,raw_y,raw_z,sampled_frequency,noise_th):
        self.raw_x = raw_x
        self.raw_y = raw_y
        self.raw_z = raw_z
        self.sampled_frequency = sampled_frequency
        self.noise_th = noise_th
        self.grad=0

    def Gradient(self,First_value, First_sample, Second_value, Second_sample):
        Value_difference = Second_value - First_value
        Sample_difference = Second_sample - First_sample
        self.grad = Value_difference / Sample_difference
        return self.grad

    def getMotionPara(self):

        print("getMotionPara")
        sample_space = (1/self.sampled_frequency)
        df=pd.DataFrame({'raw_x': self.raw_x, 'raw_y': self.raw_y, 'raw_z':self.raw_z})
        magnitude_counter = len(df.raw_x)
        d, c = signal.butter(4, 20, fs=self.sampled_frequency)
        zi = signal.lfilter_zi(d, c) #LP filter
        df['x_filt'],_ = signal.lfilter(d, c, df.raw_x, zi = zi*df.raw_x.iloc[0])
        df['y_filt'],_ = signal.lfilter(d, c, df.raw_y, zi = zi*df.raw_y.iloc[0])
        df['z_filt'],_ = signal.lfilter(d, c, df.raw_z, zi = zi*df.raw_z.iloc[0])
        df['mag'] = np.sqrt(np.square(df.x_filt)+np.square(df.y_filt)+np.square(df.z_filt))

        df['x_zero'] = df.x_filt - (df.x_filt.sum()/magnitude_counter)
        df['y_zero'] = df.y_filt - (df.y_filt.sum()/magnitude_counter)
        df['z_zero'] = df.z_filt - (df.z_filt.sum()/magnitude_counter)
        df['mag_zero_bias'] = df.mag - (df.mag.sum()/magnitude_counter)
        df['movement'] = df.mag_zero_bias>self.noise_th

        df.x_zero.loc[df.mag_zero_bias<self.noise_th] = 0
        df.y_zero.loc[df.mag_zero_bias<self.noise_th] = 0
        df.z_zero.loc[df.mag_zero_bias<self.noise_th] = 0

        counter = 0
        block_number = 0
        true_counter = 0
        start_of_movement = []
        end_of_movement = []
        df['block_number'] = 0

        while(counter < len(df.movement)): #cycle through data
            if (df.movement[counter] == True):#if data shows movement
                if (df.movement[counter-int(0.2/sample_space)] == True and df.movement[counter] == True): #if data from ten samples ago and 'now' both show movement
                    df.movement.iloc[df.movement.index[counter-int(0.2/sample_space):counter]] = True #then every sample between these samples show movement
                while(df.movement[counter]==True):#while the data shows movement
                    counter += 1 #move to the next sample
            counter += 1 # cycle to the next sample

        counter = 0
        while(counter < len(df.movement)): #cycle through data
            true_counter = 0
            if (df.movement[counter] == True): #if data shows movement
                while(df.movement[counter]==True): #while the data shows movement
                    counter += 1 #move to the next sample
                    true_counter += 1
                    #the movement is now ended, and now is best to check whether the data is a false movement
                if (true_counter < int(0.2/sample_space)): #if movement data is less than 10 samples long
                    df.movement.loc[df.movement.index[counter-true_counter:counter]] = False #then every sample between these samples shows no movement
                    #as it's a false positive, we can disregard the data, so we set the x,y,z data to 0
                    df.x_zero.iloc[df.x_zero.index[counter-true_counter:counter]] = 0
                    df.y_zero.iloc[df.y_zero.index[counter-true_counter:counter]] = 0
                    df.z_zero.iloc[df.z_zero.index[counter-true_counter:counter]] = 0
            counter += 1

        counter = 0
        while(counter < len(df.movement)): #cycle through data
            if (df.movement[counter] == True): #if data shows movement
                df.block_number += 1
                start_of_movement.append(counter-1)
                while(df.movement[counter]==True): #while the data shows movement
                    counter += 1 #move to the next sample
                end_of_movement.append(counter) #when the data shows end of movement, record index
            counter += 1 # cycle to the next sample
        end_of_movement.append(counter)

        df.x_zero = df.x_filt * df.movement
        df.y_zero = df.y_filt * df.movement
        df.z_zero = df.z_filt * df.movement

        df['r_zero'] = np.sqrt(np.square(df.x_zero)+np.square(df.y_zero)+np.square(df.z_zero))
        df['theta_zero'] = (df.y_zero / df.x_zero).fillna(0.0)
        df['phi_zero']=(np.arccos(df.z_zero / df.r_zero)).fillna(0.0)

        x = [trapz(df.x_zero[0:i],dx = sample_space) for i in range(0, len(df.x_zero))]
        y = [trapz(df.y_zero[0:i],dx = sample_space) for i in range(0, len(df.y_zero))]
        z = [trapz(df.z_zero[0:i],dx = sample_space) for i in range(0, len(df.z_zero))]

        vdf=pd.DataFrame({'x_vel': x, 'y_vel': y, 'z_vel':z})
        vdf['error_x'] = vdf.x_vel
        vdf['error_y'] = vdf.y_vel
        vdf['error_z'] = vdf.z_vel
        gradient_array_x = []
        gradient_array_y = []
        gradient_array_z = []
        movement_counter = 0
        while movement_counter < max(df.block_number):
            gradient_array_x.append(self.Gradient(vdf.error_x.iloc[start_of_movement[movement_counter]], start_of_movement[movement_counter], vdf.error_x.iloc[end_of_movement[movement_counter]], end_of_movement[movement_counter]))
            gradient_array_y.append(self.Gradient(vdf.error_y.iloc[start_of_movement[movement_counter]], start_of_movement[movement_counter], vdf.error_y.iloc[end_of_movement[movement_counter]], end_of_movement[movement_counter]))
            gradient_array_z.append(self.Gradient(vdf.error_z.iloc[start_of_movement[movement_counter]], start_of_movement[movement_counter], vdf.error_z.iloc[end_of_movement[movement_counter]], end_of_movement[movement_counter]))
            movement_counter += 1

        counter = 0
        gradient_counter = 0
        movement_counter = 0
        while(counter < len(df.movement)): #cycle through data
            if (df.movement.iloc[counter] == True) :
                while(df.movement.iloc[counter] == True):
                    vdf.error_x.iloc[counter] = gradient_array_x[gradient_counter] * (counter-start_of_movement[movement_counter]) + vdf.error_x.iloc[start_of_movement[movement_counter]]
                    vdf.error_y.iloc[counter] = gradient_array_y[gradient_counter] * (counter-start_of_movement[movement_counter]) + vdf.error_y.iloc[start_of_movement[movement_counter]]
                    vdf.error_z.iloc[counter] = gradient_array_z[gradient_counter] * (counter-start_of_movement[movement_counter]) + vdf.error_z.iloc[start_of_movement[movement_counter]]
                    counter += 1
                gradient_counter += 1
                movement_counter += 1
            counter+=1
        vdf['x_vel_edit'] = vdf.x_vel - vdf.error_x
        vdf['y_vel_edit'] = vdf.y_vel - vdf.error_y
        vdf['z_vel_edit'] = vdf.z_vel - vdf.error_z

        vdf['phi_prep'] = vdf.x_vel_edit

        counter = 0
        while(counter < len(df.movement)): #cycle through data
            if (abs(vdf.phi_prep.iloc[counter]) < 0.02):
                vdf.phi_prep.iloc[counter] = 0.0
            counter+=1

        vdf['r_vel_edit'] = np.sqrt(np.square(vdf.x_vel_edit)+np.square(vdf.y_vel_edit)+np.square(vdf.z_vel_edit))
        vdf['phi_vel_edit'] = (vdf.y_vel_edit / vdf.phi_prep).fillna(0.0)
        vdf.phi_vel_edit = vdf.phi_vel_edit.replace([np.inf, -np.inf], 0.0)
        vdf['theta_vel_edit']=(np.arccos(vdf.z_vel_edit / vdf.r_vel_edit)).fillna(0.0)

        #return df.x_zero, df.y_zero, df.z_zero, vdf.x_vel_edit, vdf.y_vel_edit, vdf.z_vel_edit
        return df.x_zero, df.y_zero, df.z_zero, df.r_zero, df.theta_zero, df.phi_zero, vdf.x_vel_edit, vdf.y_vel_edit, vdf.z_vel_edit, vdf.r_vel_edit, vdf.theta_vel_edit, vdf.phi_vel_edit
