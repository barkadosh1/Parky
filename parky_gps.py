# import necessary libraries
import subprocess
import time
from picamera import PiCamera
from datetime import datetime

# initalize values
fail_count = 0
init_lat = 0.0
init_long = 0.0
camera = PiCamera()
count = 0
open_locations = [] # list will store tuple of (longitude, latitude, north_south, east_westw, filepath, date_time)

# start a continuous while loop. We will break out of this while loop when a GPS
# connection no longer exists.
while(True):
    # run the following shell code each time through the while loop to read
    # in the GPS coordinates for a second into the parky.txt file
    # the GPS coordinates will overwrite in the file each time so that we are
    # always capturing the most updated coordinates
    cmd = 'timeout 1 stdbuf -o0 curl 172.20.10.1:11123 > parky.txt'
    process_run = subprocess.Popen(cmd, shell=True)

    # python 1 second sleep command to wait for the curl shell code to finish
    time.sleep(1)

    # read the data
    with open('parky.txt', 'r') as file:
        data = file.read()

    try:
        camera.start_preview()

        # process/split the data into relevant values
        data = data.split(',')
        timestamp = data[1]
        latitude = float(data[2])
        north_south = data[3]
        longitude = float(data[4])
        east_west = data[5]

        # if the latitude or longitude has changed by more than a specified threshold
        # we update our coordinates to the current coordinates
        # we then trigger our camera to take a photo and save it to a file path
        if abs(latitude - init_lat) > 0.0001 or abs(longitude - init_long) > 0.0001:
            init_lat = latitude
            init_long = longitude
            time.sleep(.3)
            date_time = datetime.now().strftime('%Y_%m_%d %H_%M_%S')
            file_path = '/home/pi/parky_images/image_'+date_time+'.jpg'
            camera.capture(file_path)

        fail_count = 0

    # if any error occurs in our try section, we increase the fail count by 1
    # if the fail count is ever greater than 10, we terminate the program
    # this would occur for example, if for 10 consecutive seconds, the GPS
    # connection was no longer active
    except:
        fail_count+=1
        if fail_count > 10:
            camera.stop_preview()
            print('No connection...terminating program')
            break
