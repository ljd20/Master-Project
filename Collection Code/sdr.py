from rtlsdr import *
import numpy as np
import matplotlib.pyplot as plt

# SDR class - processes SDR sampling and image creation.
class SDR:
    def __init__(self, tracking, data_size = 11, sample_rate = 3.2e6, centre_freq = 1.4e9, gain = 49.6, freq_correction = -67, tau = 1/5):
        self.tracking = tracking
        self.sdr = RtlSdr()
        self.data = np.zeros((data_size,data_size))
        self.sdr.sample_rate = sample_rate
        self.sdr.center_freq = centre_freq
        self.sdr.gain = gain
        self.sdr.freq_correction = freq_correction
        self.sdr.set_direct_sampling(0)
        self.num_samples = 2 * tau * sample_rate

    # Single scan for particular position of antenna.
    def sampling (self, az_element, el_element):
        samples = self.sdr.read_samples(self.num_samples)
        samples = samples[2500:]
        az_index = int(az_element + self.data.shape[0] // 2)
        el_index = int(-el_element + self.data.shape[1] // 2)
        avg_pwr = np.mean(abs(samples)**2)
        self.data[az_index, el_index] = avg_pwr
        print(az_index, el_index, avg_pwr)

    # Creates image of average power from the samples.
    def create_image(self):
        self.data = self.data.astype(np.float64)
        np.savetxt('radio_image_data.txt', self.data)
        fig, ax = plt.subplots()
        cax = ax.imshow(self.data, interpolation='nearest', cmap='jet', aspect='auto', origin='lower', extent=[0, self.data.shape[1], 0, self.data.shape[0]])
        cbar = fig.colorbar(cax)
        ax.axis('off') 
        plt.tight_layout()
        plt.savefig('radio_image_sun.png')
        plt.show()

    # Shut down sampling of SDR.
    def close_sdr(self):
        return
        self.sdr.close()