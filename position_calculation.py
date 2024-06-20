import ephem
import time

# PositionCalculaton class - Calculates the celestial objects positions.
class PositionCalculation:
    def __init__(self, tracking):
        self.tracking = tracking

    # Moon azimuth and elevation.
    def get_moon_position(self):
        self.tracking.location.gps_update()
        moon = ephem.Moon(self.tracking.obs)    
        print("Moon Azimuth and Elevation: ", moon.az, moon.alt)
        self.tracking.azimuth = moon.az * 180 / 3.14159
        self.tracking.elevation = moon.alt * 180 / 3.14159

    # Sun azimuth and elevation.
    def get_sun_position(self):
        self.tracking.location.gps_update()
        Sun = ephem.Sun(self.tracking.obs)
        print("Sun Azimuth and Elevation: ", Sun.az, Sun.alt)
        self.tracking.azimuth = Sun.az * 180 / 3.14159
        self.tracking.elevation = Sun.alt * 180 / 3.14159

    # Gets position of selected body.
    def get_target_position(self):                            
        if (self.tracking.gui.Track.get() == "Moon"):
            print("Getting Moon")
            self.get_moon_position()
        if (self.tracking.gui.Track.get() == "Sun"):
            print("Getting Sun")
            self.get_sun_position()
        if (self.tracking.gui.Track.get() == "Manual"):
            print("Getting manual")
            self.tracking.azimuth = ManAz
            self.tracking.elevation = ManEl  

    # Sets rotators to azimuth = 0 and elevation = 0.
    def reset_rotators(self):
        self.tracking.Ser.reset_input_buffer()
        self.tracking.Ser.reset_output_buffer()
        self.tracking.Ser.write(b'\r')
        input("Switch on Rotator Computer Controller and then press enter")
        time.sleep(1)
        self.tracking.azimuth = 0
        self.tracking.elevation = 0
        self.tracking.position_control.send_rotator_command()
        print(self.tracking.Ser.read())
        self.yaw = 0
