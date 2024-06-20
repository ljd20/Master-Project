from gui import GUI
from sdr import SDR
from raster_scanner import RasterScanner
from position_control import PositionControl
from position_calculation import PositionCalculation
from location import Location
import serial
import ephem
import cv2 as cv
import picamera
import time

# Tracking class - Top class, Processes when the cool down times happen.
class Tracking:
    def __init__(self, HPBW, data_size, sample_rate, centre_freq, gain, freq_correction, azimuth=0, elevation=90, latitude=0, longitude=0, altitude=0, yaw=0, add=0x1E, body="Sun"):
        self.azimuth = azimuth
        self.elevation = elevation
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.yaw = yaw
        self.execute_raster_scan = False
        self.obs = ephem.Observer()  
        # self.camera = picamera.PiCamera()
        self.Ser = serial.Serial('/dev/ttyUSB_DEVICE1', 9600, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
        self.gui = GUI(self)
        self.raster_scanner = RasterScanner(self, HPBW)
        self.sdr = SDR(self, data_size, sample_rate, centre_freq, gain, freq_correction)
        self.position_control = PositionControl(self)
        self.position_calculation = PositionCalculation(self)
        self.location = Location(self, add)    
        self.rotator_operation_start_time = time.time()
        self.is_paused = False
        self.cool_down_start_time = None
        self.cool_down_duration = 15 * 60 
        self.saved_azimuth = None
        self.saved_elevation = None

    # Take image from camera and save to jpg file.
    def capture_image(self):
        print("Taking Picture")
        self.camera.capture('/home/pi/Desktop/Moon.jpg')
        img = cv.imread("/home/pi/Desktop/Sun_Image_Project/Moon.jpg")
        if img is not None:
            img = cv.resize(img, (256, 256))
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  
            cv.imwrite("/home/pi/Desktop/Sun_Image_Project/Moon.jpg", img)
            img = cv.resize(img, (64, 64))
            cv.imwrite("/home/pi/Desktop/Sun_Image_Project/Moon_CNN.jpg", img)
        else:
            print("Error: Image not found.")

    # Check if computer controller is on after cool down.
    def is_controller_on(self):
        try:
            self.Ser.write(b'C2\r')
            time.sleep(1)
            response = self.Ser.readline().decode().strip()
            if response in ["AZ=-001  EL=-002", "AZ=-001  EL=-001"]:
                print("Waiting for the controller to be switched on.")
                return False
            return bool(response)
        except Exception as e:
            print(f"Error checking controller status: {e}")
            return False

    # Restart scanning process after cool down.
    def start_rotator_operation(self):
        self.rotator_operation_start_time = time.time()
        self.is_paused = False
        time.sleep(2)

    # Chooses between cool down and continue scanning.
    def check_rotator_duration(self):
        estimated_time_for_scan = 12

        if self.is_paused:
            while time.time() - self.cool_down_start_time < self.cool_down_duration or not self.is_controller_on():
                cool_down_time_left = self.cool_down_duration - (time.time() - self.cool_down_start_time)
                if cool_down_time_left > 0:
                    print(f"Rotator is paused for cool down. Time left: {int(cool_down_time_left)} seconds.")
                else:
                    print("Waiting for the controller to be switched on.")
                time.sleep(1)
            if self.is_controller_on():
                self.is_paused = False
                self.start_rotator_operation()
                self.restore_rotators()
        else:
            time_left = (5*60) - (time.time() - self.rotator_operation_start_time)
            print(f"Time left until cool down: {int(time_left)}")
            if time_left < estimated_time_for_scan:
                self.is_paused = True
                self.cool_down_start_time = time.time()
                self.save_rotator_angles()
                self.shutdown_rotators()
                self.check_rotator_duration()

    # Save the rotator angles before cool down for recalibration.
    def save_rotator_angles(self):
        try:
            self.Ser.write(b'AZ?\r')
            time.sleep(1)
            self.saved_azimuth = self.Ser.readline().decode().strip()
            self.Ser.write(b'EL?\r')
            time.sleep(1)
            self.saved_elevation = self.Ser.readline().decode().strip()
            print(f"Saved azimuth: {self.saved_azimuth}, elevation: {self.saved_elevation}")
        except Exception as e:
            print(f"Error saving rotator angles: {e}")

    # Restore the rotator angles after cool down for recalibration.
    def restore_rotators(self):
        if self.saved_azimuth and self.saved_elevation:
            try:
                self.Ser.write(f'AZ{self.saved_azimuth}\r'.encode())
                time.sleep(1)
                self.Ser.write(f'EL{self.saved_elevation}\r'.encode())
                print(f"Restored azimuth to {self.saved_azimuth} and elevation to {self.saved_elevation}")
            except Exception as e:
                print(f"Error restoring rotator angles: {e}")

    # Show users the cool down has started.
    def shutdown_rotators(self):
        print("Shutting down rotators for cooldown.")
            
    # Close the GUI interface and Serial communication.
    def close_application(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.Ser.close()
            self.gui.root.destroy()

    # Executes the main loop of tracking and raster scanning.
    def main_loop(self):
        self.location.recalibrate_system()
        self.check_rotator_duration()
        # self.capture_image()
        self.position_calculation.get_target_position()
        self.position_control.send_rotator_command()
        try:
            user_input = input("Execute raster scan? True or False ")
            if user_input.lower() in ['true', 'false']:
                self.execute_raster_scan = user_input.lower() == 'true'
            else:
                raise ValueError("Invalid input")
        except ValueError:
            self.execute_raster_scan = False
        print(self.execute_raster_scan)
        self.gui.gui_update() 
        if self.execute_raster_scan:
            self.raster_scanner.move_azimuth()
        self.gui.root.after(1000, self.main_loop)
