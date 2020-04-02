import numpy as np
import pandas as pd
from scipy import signal


class NoiseThreshold:
    def __init__(self,raw_x,raw_y,raw_z,sampled_frequency):
        self.raw_x = raw_x
        self.raw_y = raw_y
        self.raw_z = raw_z
        self.sampled_frequency = sampled_frequency

    def getThreshold(self):
        nf = pd.DataFrame({'x': self.raw_x, 'y': self.raw_y, 'z':self.raw_z})
        #nf.head()
        magnitude_counter = len(nf.x)
    # Low Pass filter the data
        d, c = signal.butter(4, 20, fs=self.sampled_frequency)
        zi = signal.lfilter_zi(d, c) #LP filter

        nf['x_filt'],_ = signal.lfilter(d, c, nf.x, zi = zi*nf.x.iloc[0])
        nf['y_filt'],_ = signal.lfilter(d, c, nf.y, zi = zi*nf.y.iloc[0])
        nf['z_filt'],_ = signal.lfilter(d, c, nf.z, zi = zi*nf.z.iloc[0])
        nf['mag'] = np.sqrt(np.square(nf.x_filt)+np.square(nf.y_filt)+np.square(nf.z_filt))
        bias_x = nf.x_filt.sum()/magnitude_counter
        bias_y = nf.y_filt.sum()/magnitude_counter
        bias_z = nf.z_filt.sum()/magnitude_counter
        bias_mag = nf.mag.sum()/magnitude_counter
        nf['x_zero_bias'] = nf.x_filt - bias_x
        nf['y_zero_bias'] = nf.y_filt - bias_y
        nf['z_zero_bias'] = nf.z_filt - bias_z
        nf['mag_zero_bias'] = nf.mag - bias_mag
        nf['x_sq'] = np.square(nf.x_zero_bias)
        nf['y_sq'] = np.square(nf.y_zero_bias)
        nf['z_sq'] = np.square(nf.z_zero_bias)
        th = np.sqrt((nf[['x_sq','y_sq','z_sq']].max()).sum())
        return th

