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

settings_file = open('settings.json', 'r')
settings = json.load(settings_file)

EMAIL = settings['email']
NOTIFY = settings['email_notifications']
MIN_AREA = int(settings['min_contour'])  #Min area of contours to detect as motion
camera = cv2.VideoCapture(0)        #Initialize the webcam for videocapture
firstFrame = None                   #Set the firstframe to none

if NOTIFY:
    #Authenticate client with gmail api
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

#mes = create_message(EMAIL, EMAIL, 'Motion Detected!', "Motion has been detected by your security webcam!")
#send_message(service, "me", mes)

wait_for_focus = True
time_detected = None
motion_detected = False

while True:
    #let the cmamera focus
    if wait_for_focus:
        time.sleep(2)

    #read in a frame from the camera
    (grabbed, frame) = camera.read()
    if not grabbed:
        break

    #Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    #set the firstframe if not set
    if firstFrame is None:
        firstFrame = gray
        wait_for_focus = False
        continue

    #Find the difference between the current frame and the first frame. Difference = "motion"
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    #Find all the contours in the current frame difference
    _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #If any of the contours are larger than the minimum area...
    for c in cnts:
        if cv2.contourArea(c) < MIN_AREA:
            continue

        #Surround the contour with a rectangle!
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    #Write time and date
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    #Display the frame
    cv2.imshow("Security Feed", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
