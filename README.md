# Rowling Hardware: Raspberry Pi Image Capture and Upload

## Overview
Rowling Hardware is responsible for capturing images of agricultural fields using a Raspberry Pi with a camera module. These images are then uploaded to a Google Drive folder for further processing and analysis.

## Hardware Components
- Raspberry Pi
- Camera Module
- Push Button (for starting and stopping image capture)
- Character LCD Display (for user feedback)

## Dependencies
- picamera: Library for controlling the Raspberry Pi camera module.
- RPi.GPIO: Library for accessing GPIO pins on the Raspberry Pi.
- RPLCD: Library for controlling LCD displays.
- helpers.py: Helper functions for handling image capture, compression, and upload.

## Setup
1. Connect the camera module to the Raspberry Pi.
2. Connect the push button to a GPIO pin on the Raspberry Pi.
3. Connect the character LCD display to the Raspberry Pi.

## Configuration
- MAX_IMAGES: Maximum number of images to capture.
- period: Time interval between image captures (in seconds).
- RESOLUTION: Resolution of the captured images.
- quality: Image compression quality (85 means compress from 100 Kb into ~15 KB).

## Usage
1. Ensure that the hardware components are properly connected.
2. Install the necessary dependencies by running `pip install picamera RPi.GPIO RPLCD`.
3. Run the Python script `capture_and_upload.py` using `python capture_and_upload.py`.
4. Press the push button to start image capture. Press again to stop.
5. Images will be captured and uploaded to a Google Drive folder.

## Monitoring
- The LCD display provides feedback on the current state (e.g., capturing images, uploading).
- LED indicators or additional displays can be added for visual feedback.

## Contributing
Contributions to improve the functionality or add new features are welcome! Please submit a pull request with your changes.

## License
This project is licensed under the MIT License.


