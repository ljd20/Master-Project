import time

# PositionControl class sends positions to the rotators.
class PositionControl:
    def __init__(self, tracking):
        self.tracking = tracking
        self.clear_buffers()

    # Ensure the buffers are clear for next command.
    def clear_buffers(self):
        self.tracking.Ser.reset_input_buffer()
        self.tracking.Ser.reset_output_buffer()

    # Sends the current azimuth and elevation to the computer controller.
    def send_rotator_command(self):
        try:
            self.tracking.azimuth = round(self.tracking.azimuth - self.tracking.yaw)
            self.tracking.elevation = round(self.tracking.elevation)
            self.tracking.azimuth = (self.tracking.azimuth % 360 + 360) % 360
            azimuth_serial = str(self.tracking.azimuth).zfill(3)
            if self.tracking.elevation > 180:
                elevation_serial = "180"
            elif self.tracking.elevation < 0:
                elevation_serial = "000"
            else:
                elevation_serial = str(self.tracking.elevation).zfill(3)
            print("Sending: w" + azimuth_serial + " " + elevation_serial + "\r")
            Cmd = bytes("w" + azimuth_serial + " " + elevation_serial + "\r", 'utf-8')
            self.tracking.Ser.write(Cmd)
            time.sleep(1.5)
            self.wait_for_position_match(self.tracking.azimuth, self.tracking.elevation)
        except Exception as e:
            print(f"Error in send_rotator_command: {e}")
        
    # Reads from computer controller the current angles of the rotators.
    def read_current_angles(self):
        try:
            self.tracking.Ser.reset_input_buffer()
            self.tracking.Ser.reset_output_buffer()
            command = b'C2\r'
            self.tracking.Ser.write(command)
            time.sleep(1.5)
            max_retries = 3
            for _ in range(max_retries):
                self.tracking.Ser.write(b'\r')
                time.sleep(1.5)
                response = self.tracking.Ser.readline().decode().strip()
                print(f"C2 Response: {response}")
                if response.startswith("AZ=") and " EL=" in response:
                    parts = response.split()
                    az = int(parts[0].split('=')[1])
                    el = int(parts[1].split('=')[1])
                    return az, el
                else:
                    print("Invalid response received from C2 command. Retrying...")
                    time.sleep(1)
            print("Failed to get valid response after multiple retries.")
            return None, None
        except Exception as e:
            print(f"Error while sending C2 command: {e}")
            return None, None

    # Waits until the rotators are in correct positions.
    def wait_for_position_match(self, target_azimuth, target_elevation, tolerance=2):
        while True:
            az, el = self.read_current_angles()
            time.sleep(2)
            if az is not None and el is not None:
                if self.tracking.execute_raster_scan:
                    if abs(az - target_azimuth) <= 1 and abs(el - target_elevation) <= 1 :
                        break
                    else:
                        time.sleep(5)
                        self.tracking.raster_scanner.send_raster_command()
                else:
                    if abs(az - target_azimuth) <= tolerance and abs(el - target_elevation) <= tolerance:
                        break
            else:
                print("Failed to get current position using C2 command.")
