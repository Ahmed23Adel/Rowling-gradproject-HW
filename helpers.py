import socket
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD
import requests
import json
import time
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from PIL import Image

def compress_image(input_path, output_path, quality=85):
    """
    Compress the image and save it to the output path.
    
    Parameters:
    - input_path: Path to the input image file.
    - output_path: Path to save the compressed image file.
    - quality: Quality of the output image (1-100). Lower value means higher compression.
    """
    with Image.open(input_path) as img:
        img.save(output_path, "JPEG", optimize=True, quality=quality)


# Function compresses an image and prints comparison before and after compression
def compress(image_path, quality):
        # print original image size
        original_size = os.path.getsize(image_path)
        print(f"Original size: {original_size} bytes")
        # compress the image and print compressed image size
        compress_image(image_path, image_path, quality=quality)
        compressed_size = os.path.getsize(image_path)
        size_diff = original_size - compressed_size
        size_diff_percentage = (size_diff / original_size) * 100
        print(f"Compressed size: {compressed_size} bytes")
        print(f"Size reduced by: {size_diff} bytes ({size_diff_percentage:.2f}%)")
        return size_diff_percentage
        


# Function to pass the current state to the website dashboard
def set_state(state):
    # Define the endpoint
    url = "http://rowling-backend3.eastus.azurecontainer.io:8000/api/v1/update_car_state"

    state_payload_mapping = {
        'collecting_images': 0,
        'uploading_images': 1,
        'evaluating_results': 2
        }
    # Define the payload
    payload = {
        "current_state": state_payload_mapping[state]
    }


    # Make the POST request
    response = requests.put(url, data=json.dumps(payload))

    # Check the response status code
    if response.status_code == 200:
        print("Request was successful")
        print("Response:", response.json())
    else:
        print(f"Request failed with status code: {response.status_code}")
        print("Response:", response.text)
        
        
# Function to check whether the raspberry pi is connected to WiFi
def is_connected():
    try:
        # Connect to the host -- tells us if the host is actually reachable
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        pass
    return False


# Function to get the LCD instance
def get_lcd():
    lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, 
                  cols=16, rows=2, dotsize=8, 
                  charmap='A00', auto_linebreaks=True, backlight_enabled=True)
    lcd.clear()
    return lcd


# Function divides content into 2 lines on LCD
def write2lines(lcd, word1, word2):
    # both words should not be longer than 16 character
    lcd.clear()
    lcd.write_string(word1)
    lcd.cursor_pos = (1, 0)
    lcd.write_string(word2)


def authenticate_with_google(credentials_file):
    """
    Authenticates with Google using a service account and returns the credentials object.

    Args:
    - credentials_file: Path to the JSON file containing service account credentials.

    Returns:
    - credentials: Credentials object obtained from the service account key file.
    """
    try:
        # Load service account credentials from file
        credentials = ServiceAccountCredentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])

        return credentials
    except Exception as e:
        print("Error:", e)
        return None


def create_folder(service, parent_folder_id, folder_name):
    """
    Creates a folder in Google Drive.

    Args:
    - service: Drive API service object.
    - parent_folder_id: ID of the parent folder.
    - folder_name: Name of the folder to create.

    Returns:
    - folder_id: ID of the created folder.
    """
    folder_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]}
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')


# Functions returns needed info to upload to google drive folder
def get_drive_info(credentials_file_path, drive_link):
    # Authenticate with Google Drive
    credentials = authenticate_with_google(credentials_file_path)

    # Build the Drive API service
    service = build('drive', 'v3', credentials=credentials)
    
    # Get the ID of the parent folder
    parts = drive_link.split('/') # Split the URL by '/'
    
    # Get the last part, which contains the folder ID
    parent_folder_id = parts[-1].split('?')[0]

    # Create a folder with the current date
    folder_name = time.strftime('%Y-%m-%d')
    folder_id = create_folder(service, parent_folder_id, folder_name)
    return service, folder_id



def upload_image(service, folder_id, image_path, image_name):
    """
    Uploads an image to a folder in Google Drive.

    Args:
    - service: Drive API service object.
    - folder_id: ID of the folder to upload the image to.
    - image_path: Path to the image file.
    - image_name: Name of the image.

    Returns:
    - None
    """
    print(f"Attempting to upload image: {image_path}")  # Add this line to print the file path
    try:
        file_metadata = {'name': image_name, 'parents': [folder_id]}
        media = MediaFileUpload(image_path, mimetype='image/jpeg')
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Successfully uploaded image: {image_path}")  # Add this line to print the file path
    except Exception as e:
        print(f"Error uploading image: {e}")

 
            