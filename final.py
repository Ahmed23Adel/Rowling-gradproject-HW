import picamera
import time
import os
import random
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD
import helpers
from helpers import get_drive_info, create_folder, upload_image

# Code Parameters
MAX_IMAGES = 30
period = 1
RESOLUTION = (1920, 1080)
# Parameter to control compression (85 means compress from 100 Kb into ~15 KB)
quality = 85 
start_flag = False
stop_capture = False

# LCD setup
lcd = helpers.get_lcd()

# GPIO setup for push buttons
BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def start_stop_capture_button_callback(channel):
    global start_flag, stop_capture
    if not start_flag:
        lcd.clear()
        lcd.write_string("Starting capture")
        start_flag = True
        time.sleep(2)
    else:
        helpers.write2lines(lcd, "Stopping capture", "due to interrupt!")
        stop_capture = True
        time.sleep(2)

# Add event detect for button press
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=start_stop_capture_button_callback, bouncetime=3000)


# Check for internet connection
while not helpers.is_connected():
    helpers.write2lines(lcd, "Retry your WiFi", "connection")
    time.sleep(1)
# If wifi is connected, then break the loop    
helpers.write2lines(lcd, "WiFi Connected", "successfully!")    
time.sleep(2) # To give user time to read lcd


# Loop till user gives order to start
helpers.write2lines(lcd, "Waiting button", "Press to start")
while not start_flag:
    time.sleep(0.1)


if __name__ == '__main__':
    try:
        # Determine the directory of the main script
        script_directory = os.path.dirname(os.path.abspath(__file__))
        folder_name = time.strftime("%a, %d %b %Y %H:%M:%S")  # (e.g Fri, 07 Jun 2024 16:06:43)
        folder_path = os.path.join(script_directory, folder_name)

        # Create the local folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            os.chmod(folder_path, 0o777) #to be able to control it from GUI


        # Initialize the camera
        with picamera.PiCamera() as camera:
            # Set resolution if needed
            camera.resolution = RESOLUTION
            # Un/comment this when it is needed to live view the camera output on a screen
            camera.start_preview()
            
            
            # Send the state to the website dashboard
            helpers.set_state('collecting_images')
            image_num = 0  # counter
            # Generate a random integer array simulating the zone numbers
            random_zones = random.sample(range(1,MAX_IMAGES+1),MAX_IMAGES)
            while image_num < MAX_IMAGES and not stop_capture:
                zone_num = random_zones[image_num]

                # Tag each image with the time it is taken at (e.g 10:35)
                current_time = time.strftime("%H:%M")

                # Generate image filename with zone and time (e.g Zone_5_10:35.jpg)
                image_name = f"Zone_{zone_num}_{current_time}.jpg"

                # Capture image and save it in image_path with image_name 
                image_path = os.path.join(folder_path, image_name)
                camera.capture(image_path)

                # Increment counter
                image_num += 1
                helpers.write2lines(lcd, f"Image {image_num} taken", "successfully!")
                
                # Removing a portion (400 ms) from waiting time since it
                # is already consumed during taking image
                time.sleep(abs(period - 0.4))
            
            # Finished Capturing
            helpers.write2lines(lcd, f"{image_num} images taken", "successfully!")
            time.sleep(2)
            camera.stop_preview()
            

            # Authenticate and get info from google drive
            drive_link = 'https://drive.google.com/drive/folders/1w8Y2YonL3nCC6tOIs1oTEiOAEH8CSGoE?usp=drive_link'
            credentials_file_name = "model-union-418902-944eade71c87.json"
            credentials_file_path = os.path.join(script_directory, credentials_file_name)
            service, drive_folder_id = get_drive_info(credentials_file_path, drive_link)
            
            # Begin uploading
            helpers.set_state('uploading_images')
            helpers.write2lines(lcd, f"Upload in", "progress")
            for image_num, image_name in enumerate(os.listdir(folder_path)):
                image_path = os.path.join(folder_path, image_name)
                # Compress the image to save Bandwidth
                size_diff_percentage = helpers.compress(image_path, quality)
                helpers.write2lines(lcd, f"Image {image_num+1} size is", f"reduced by {size_diff_percentage:.1f}%")
                # Upload
                helpers.upload_image(service, drive_folder_id, image_path, image_name)
                helpers.write2lines(lcd, f"Image {image_num+1} uploaded", "successfully!")
            # Finished uploading
            helpers.write2lines(lcd, f"{image_num+1} images have", " been uploaded!")
                
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(2)
    finally:
        helpers.set_state('evaluating_results')
        helpers.write2lines(lcd, 'Best wishes from', '   Rowling <3   ')
        GPIO.cleanup()
        print("GPIO cleanup done")

