from tracking import Tracking
import config

# main calls the system.
def main():
    # Configuration set up.
    HPBW = config.HPBW
    data_size = config.data_size
    sample_rate = config.sample_rate
    centre_freq = config.centre_freq
    gain = config.gain
    freq_correction = config.freq_correction
    
    # Initialise classes.
    module = Tracking(HPBW, data_size, sample_rate, centre_freq, gain, freq_correction)
    module.gui.initialise_tracking_method()
    module.position_calculation.reset_rotators()
    manual_input = input('Automatically Detect Location? Y/N ')
    if (manual_input == 'Y' or manual_input == 'y'):
        module.location.auto_location()
    else:
        module.location.manual_location()

    module.gui.root.after(1000, module.main_loop)
    module.gui.root.protocol("WM_DELETE_WINDOW", module.close_application)
    module.gui.root.mainloop()

if __name__ == '__main__':
    main()
