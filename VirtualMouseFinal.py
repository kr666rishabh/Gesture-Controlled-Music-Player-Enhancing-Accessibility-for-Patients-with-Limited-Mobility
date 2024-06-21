import cv2
import numpy as np
import time
import HandTracking as ht
import autopy
import os  # Import os module for opening Spotify

# Variables needed
pTime = 0               # For FPS
width = 900             # Camera width
height = 500            # Camera height
frameR = 100            # Frame
smoothening = 8         # Smoothening Factor
prev_x, prev_y = 0, 0   # Previous x and y coordinates
curr_x, curr_y = 0, 0   # Current x and y coordinates
click_registered = False  # Flag to track if click has been registered

cap = cv2.VideoCapture(0)   # Fetching video feed from the webcam

cap.set(3, width)           # Adjust window size
cap.set(4, height)

detector = ht.handDetector(maxHands=1)      # Detects one hand max
screen_width, screen_height = autopy.screen.size()      # Fetch screen size

# Adjusting starting position of gesture window higher for better bottom edge detection
frame_x = frameR
frame_y = frameR - 100

# Open Spotify
os.system("spotify")  # This command will open Spotify if it's installed and set up properly

while True:     # Loop until esc key press
    success, img = cap.read()

    # success = cv2.flip(success, 1)        # experiments to show flipped image
    # img = cv2.flip(img, 1)

    img = detector.findHands(img)                       # Find hand
    lmlist, bbox = detector.findPosition(img)           # Hand position detection

    if len(lmlist)!=0:
        x1, y1 = lmlist[8][1:]
        x2, y2 = lmlist[12][1:]

        fingers = detector.fingersUp()      # Fingers' orientation check
        cv2.rectangle(img, (frame_x, frame_y), (width - frameR, height - frameR), (255, 0, 255), 2)   # Creating gesture window
        if fingers[1] == 1 and fingers[2] == 0:     # If index up & middle down
            x3 = np.interp(x1, (frame_x, width-frameR), (0, screen_width))
            y3 = np.interp(y1, (frame_y, height-frameR), (0, screen_height))

            curr_x = prev_x + (x3 - prev_x)/smoothening
            curr_y = prev_y + (y3 - prev_y) / smoothening

            autopy.mouse.move(screen_width - curr_x, curr_y)    # Cursor movement active
            cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
            prev_x, prev_y = curr_x, curr_y

        if fingers[1] == 1 and fingers[2] == 1:     # If both index & middle is up
            length, img, lineInfo = detector.findDistance(8, 12, img)

            if length < 40 and not click_registered:     # If both fingers really close and click not registered(flag check)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()    # Perform click
                click_registered = True  # Set click flag to True

            elif length >= 40:  # If fingers moved away
                click_registered = False  # Reset click flag to False

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) == 27:    # ASCII(ESC)=27; If ESC pressed, release camera access, kill all windows
        cap.release()
        cv2.destroyAllWindows()
