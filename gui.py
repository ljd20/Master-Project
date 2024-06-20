import datetime
import ephem
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# GUI class - TKInter setup.
class GUI:
    def __init__(self, tracking):
        self.tracking = tracking
        self.initialise_tkinter()
        self.initialise_objects()
        self.create_labels()
        self.setup_gui_grid()
        self.initialise_gui_buttons()

    # Initialize tkinter module.
    def initialise_tkinter(self):
        self.root = tk.Tk()
        self.manual_calibration = tk.IntVar()

    # Tracking Bodies Setup.
    def initialise_objects(self):
        self.Track = tk.StringVar()
        self.Method = tk.StringVar()
        self.Bodies = ["Moon", "Sun", "Manual"]
        self.Methods = ["Lookup Table", "Neural Network (Moon Only)"]

    # Initialize labels.
    def create_labels(self):
        self.TrackMenu = tk.OptionMenu(self.root, self.Track, *self.Bodies)

        self.LatLabel = tk.Label(self.root, text="Latitude:")
        self.LongLabel = tk.Label(self.root, text="Longitude:")
        self.AltLabel = tk.Label(self.root, text="Altitude:")
        self.AzLabel = tk.Label(self.root, text="Target Azimuth")
        self.ElLabel = tk.Label(self.root, text="Target Elevation:")
        self.TrackLabel = tk.Label(self.root, text="Tracking:")
        self.MethodLabel = tk.Label(self.root, text="Detection Method:")
        self.ManAzLabel = tk.Label(self.root, text='Manually Set Azimuth:')
        self.ManElLabel = tk.Label(self.root, text='Manually Set Elevation:')
        self.c1 = tk.Checkbutton(self.root, text='Automatically Calibrate Azimuth? Warning - Magnetometer is Inaccurate', variable=self.manual_calibration, onvalue=1, offvalue=0)
        self.ChangeTime = tk.Label(self.root, text='Edit Time (YYYY-MM-DD HH:MM):')

        self.LatDisplay = tk.Label(self.root, text='0')
        self.LongDisplay = tk.Label(self.root, text='0')
        self.AltDisplay = tk.Label(self.root, text="0")
        self.AzDisplay = tk.Label(self.root, text="0")
        self.ElDisplay = tk.Label(self.root, text="0")
        self.az = tk.OptionMenu(self.root, self.Track, *self.Bodies)
        self.MethodMenu = tk.OptionMenu(self.root, self.Method, *self.Methods)
        self.ManAzEntry = tk.Entry(self.root)
        self.ManElEntry = tk.Entry(self.root)
        self.TimeEntry = tk.Entry(self.root)

        self.picture = tk.Label(self.root, image=ImageTk.PhotoImage(Image.open("/home/pi/Desktop/Sun_Image_Project/Moon.jpg")))

    # Setting position of TK Labels on GUI.
    def setup_gui_grid(self):
        self.LatLabel.grid(row=0, column=0)
        self.LongLabel.grid(row=1, column=0)
        self.AltLabel.grid(row=2, column=0)
        self.AzLabel.grid(row=3, column=0)
        self.ElLabel.grid(row=4, column=0)
        self.TrackLabel.grid(row=5, column=0)
        self.MethodLabel.grid(row=6, column=0)
        self.ManAzLabel.grid(row=7, column=0)
        self.ManElLabel.grid(row=8, column=0)
        self.ChangeTime.grid(row=9, column=0)
        self.c1.grid(row=10, column=0, columnspan=3)

        self.LatDisplay.grid(row=0, column=1)
        self.LongDisplay.grid(row=1, column=1)
        self.AltDisplay.grid(row=2, column=1)
        self.AzDisplay.grid(row=3, column=1)
        self.ElDisplay.grid(row=4, column=1)
        self.TrackMenu.grid(row=5, column=1)
        self.MethodMenu.grid(row=6, column=1)
        self.ManAzEntry.grid(row=7, column=1)
        self.ManElEntry.grid(row=8, column=1)
        self.TimeEntry.grid(row=9, column=1)
        self.picture.grid(row=0, column=2, rowspan=7)

    # Types of tracking and objects.
    def initialise_tracking_method(self):
        self.Track.set(self.Bodies[1])
        self.Method.set(self.Methods[0])

    # Updates the time if user wishes to change it from initial input.
    def update_time_gui(self):                                                  
        NewTime = self.TimeEntry.get()
        print(type(NewTime))
        StartTime = datetime.datetime.now() 
        Time0 = NewTime + ':' + '00'
        print(Time0)
        self.tracking.obs.date = ephem.Date(Time0)

    # Allows user to manually set Azimuth and Elevation.
    def set_manual_azimuth_elevation(self):                                                    
        self.tracking.azimuth = float(self.ManAzEntry.get())
        self.tracking.elevetaion = float(self.ManElEntry.get())
        print(self.tracking.azimuth)

    # Initialises the Button on the GUI.
    def initialise_gui_buttons(self): 
        self.EnterButton = tk.Button(self.root, text = 'Enter Manual Az/El', command = self.set_manual_azimuth_elevation)
        self.UpdateTime = tk.Button(self.root, text = 'Set Time', command = self.update_time_gui)
        self.EnterButton.grid(row = 7, column = 2)
        self.UpdateTime.grid(row = 9, column = 2)   

    # Updates the GUI to new values.
    def gui_update(self): 
        print("Updating GUI")
        self.LatDisplay.configure(text = self.tracking.latitude)
        self.LongDisplay.configure(text = self.tracking.longitude)
        self.AltDisplay.configure(text = self.tracking.altitude)
        self.AzDisplay.configure(text = self.tracking.azimuth)
        self.ElDisplay.configure(text = self.tracking.elevation)
        self.AltDisplay.configure(text = self.tracking.altitude)
        image = Image.open("/home/pi/Desktop/Sun_Image_Project/Moon.jpg")
        photo = ImageTk.PhotoImage(image)
        self.picture.configure(image = photo)
        self.picture.image = photo