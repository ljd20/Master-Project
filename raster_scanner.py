import time
import numpy as np

# RasterScanner class performs the raster scanning algorithm.
class RasterScanner:
    def __init__(self, tracking, HPBW):
        self.tracking = tracking
        self.raster_azimuth = 0
        self.raster_elevation = 0
        self.hpbw = HPBW

    # Adjust Sun position angles by current raster position.
    def update_rotator_position(self, delta_azimuth, delta_elevation):
        self.raster_azimuth = self.tracking.azimuth + delta_azimuth
        self.raster_elevation = self.tracking.elevation + delta_elevation
        self.send_raster_command()

    # Loops through all variations in raster elevation angles.
    def move_elevation(self, delta_azimuth):
        for delta_elevation in np.arange(round(self.hpbw), -round(self.hpbw)-1, -1):
            self.tracking.check_rotator_duration()
            self.tracking.position_calculation.get_target_position()
            self.update_rotator_position(delta_azimuth, delta_elevation)
            self.tracking.sdr.sampling(delta_azimuth, delta_elevation)
            # self.tracking.capture_image()

    # Loops through all variations in raster azimuth angles.
    def move_azimuth(self):
        for delta_azimuth in np.arange(-round(self.hpbw), round(self.hpbw)+1, 1):
            self.tracking.check_rotator_duration()
            self.move_elevation(delta_azimuth)
            print("Finished scanning")
        self.tracking.sdr.close_sdr()
        self.tracking.sdr.create_image()

    # Sends the current raster azimuth and elevation to the computer controllers.
    def send_raster_command(self):
        try:
            self.raster_azimuth = round(self.raster_azimuth - self.tracking.yaw)
            self.raster_elevation = round(self.raster_elevation)
            self.raster_azimuth = (self.raster_azimuth % 360 + 360) % 360
            azimuth_serial = str(self.raster_azimuth).zfill(3)
            if self.raster_elevation > 180:
                elevation_serial = "180"
            elif self.raster_elevation < 0:
                elevation_serial = "000"
            else:
                elevation_serial = str(self.raster_elevation).zfill(3)
            print("Sending: w" + azimuth_serial + " " + elevation_serial + "\r")
            Cmd = bytes("w" + azimuth_serial + " " + elevation_serial + "\r", 'utf-8')
            self.tracking.Ser.write(Cmd)
            time.sleep(1.5)
            self.tracking.position_control.wait_for_position_match(self.raster_azimuth, self.raster_elevation)
        except Exception as e:
            print(f"Error in send_raster_command: {e}")