#Motion detection code originally written by Adrian Rosebrock, modified by Matthew Mawby
#Adrian's original code can be found here: http://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/

from authenticate import get_credentials
from mail import create_message
from mail import send_message
from apiclient import discovery
import httplib2
import cv2
import datetime
import time
import json
import sys

settings_file = open('settings.json', 'r')
settings = json.load(settings_file)

SECONDS = int(settings['record_time'])
RES_X = int(settings['xres'])
RES_Y = int(settings['yres'])
EMAIL = settings['email']
NOTIFY = settings['email_notifications']
MIN_AREA = int(settings['min_contour'])  #Min area of contours to detect as motion
camera = cv2.VideoCapture(0)        #Initialize the webcam for videocapture
backFrame = None                   #Set the backFrame to none

# Define the codec for video writing
fourcc = cv2.VideoWriter_fourcc(*'XVID')

"""
#Set the capture resolution & check it was set properly
x_res_set = camera.set(3, RES_X)
y_res_set = camera.set(4, RES_Y)
if not x_res_set and y_res_set:
    sys.stderr.write("Failed to set frame resolution\n")
    sys.exit(0)
"""


if NOTIFY:
    #Authenticate client with gmail api
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

wait_for_focus = True
time_detected = None
motion_detected = False
out = None

while True:
    #let the cmamera focus
    if wait_for_focus:
        time.sleep(2)

    #read in a frame from the camera
    (grabbed, frame) = camera.read()
    if not grabbed:
        break

    if motion_detected:
        if out is not None:
            framecopy = frame
            #Write time and date
            cv2.putText(framecopy, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            out.write(framecopy)
        if datetime.datetime.now() >= time_detected + datetime.timedelta(seconds=SECONDS):
            motion_detected = False
            time_detected = None
            out.release()
            print "Motion Detection Ended"

    #Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    #set the backFrame if not set
    if backFrame is None:
        backFrame = gray
        wait_for_focus = False
        continue

    #Find the difference between the current frame and the first frame. Difference = "motion"
    frameDelta = cv2.absdiff(backFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    #Find all the contours in the current frame difference
    _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #Loop through all contours in the frame differences
    for c in cnts:
        #If the contour isn't large enough
        if cv2.contourArea(c) < MIN_AREA:
            continue

        if not motion_detected and time_detected is None:
            print "Motion Detected!"
            #Create an image and send it
            cv2.imwrite(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")+".jpg", frame)
            mes = create_message(EMAIL, EMAIL, 'Motion Detected!', "Motion has been detected by your security webcam!", datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")+".jpg")
            send_message(service, "me", mes)
            #Flag motion_detection as true and begin video recording
            motion_detected = True
            time_detected = datetime.datetime.now()
            fname = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")+'_WebCurity.avi'
            out = cv2.VideoWriter(fname, fourcc, 20.0, (RES_X, RES_Y))

        #Surround the contour with a rectangle!
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    #Write time and date
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    #Display the frame
    cv2.imshow("Security Feed", frame)

    #if there's no motion in the frame, set the background to the current frame
    if not motion_detected:
        backFrame = gray

    #Press q to quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
