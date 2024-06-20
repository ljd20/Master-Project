import datetime
import ephem
import math
import smbus
from pa1010d import PA1010D
import time

# Location class - deals with GPS and manual locations.
class Location:
    def __init__(self, tracking, add):
        self.tracking = tracking
        self.gps = PA1010D()
        self.bus = smbus.SMBus(1)
        self.add = add
        self.StartTime = datetime.datetime.now()

    # Transform data into twos complement.
    def twos_complement(self, data):
        if data >= 32768:
            return data - 65536
        else:
            return data

    # Update the GUI settings.
    def gps_update(self):
        self.gps.update()
        if (self.gps.data['altitude'] is not None):
            latitude = self.gps.data['latitude']
            longitude = self.gps.data['longitude']
            altitude = self.gps.data['altitude']
            self.tracking.obs.lat = latitude
            self.tracking.obs.long = longitude
            self.tracking.obs.elevation = altitude
        current_time = datetime.datetime.now()
        self.tracking.obs.date = ephem.Date(current_time)

    # Sets up new values for position.
    def recalibrate_system(self):
        print("Setting Offsets")
        self.gps_update()
        if (self.tracking.gui.manual_calibration.get() == 1):
            self.bus.write_byte_data(self.add, 0x60, 0x80)
            self.bus.write_byte_data(self.add, 0x62, 0x01)
            val0 = self.bus.read_byte_data(self.add, 0x68)
            val1 = self.bus.read_byte_data(self.add, 0x69)
            val2 = self.bus.read_byte_data(self.add, 0x6A)
            val3 = self.bus.read_byte_data(self.add, 0x6B)
            x_raw = self.twos_complement(float(val1 << 8 | val0))
            y_raw = self.twos_complement(float(val3 << 8 | val2))
            yaw = math.atan2(y_raw, x_raw) * 180 / 3.14159
            if yaw < 0:
                yaw = yaw + 360
        else:
            yaw = 0

    # Get updated location from GPS Unit.
    def auto_location(self):
        result = self.gps.update()
        while (self.gps.data['altitude'] is None):
            print('Connecting to GPS')
            result = self.gps.update()
            time.sleep(10.0)
        self.tracking.latitude = self.gps.data['latitude']
        self.tracking.longitude = self.gps.data['longitude']
        self.tracking.altitude = self.gps.data['altitude']

    # Get manual inputted location from user.
    def manual_location(self):
        self.tracking.latitude = input('Latitude: ')
        self.tracking.longitude = input('Longitude: ')
        self.tracking.altitude = float(input('Altitude: '))
        year = input('Year(YYYY):')
        month = input('Month(MM) :')
        day = input('Day(DD):')
        hour = input('Hour(HH) :')
        minute = input('Minute(MM) :')
        self.StartTime = datetime.datetime.now()
        current_time = year + '-' + month + '-' + day + ' ' + hour + ':' + minute + ':' + '00'
        current_time = datetime.datetime.now()
        self.tracking.obs.long = self.tracking.longitude
        self.tracking.obs.lat = self.tracking.latitude
        self.tracking.obs.elevation = self.tracking.elevation
        self.tracking.obs.date = ephem.Date(current_time)
