"""
    data set: http://www.cim.mcgill.ca/~epiuze/?lang=En&page=COMP558w12
    face detection: https://realpython.com/blog/python/face-detection-in-python-using-a-webcam/
"""

import cv2
import numpy as np
import os
import operator
from ann import Estimation

width = height = 256

# Create the haar cascade
cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

imagePath = "dataset"
inputs = []
targets = []

# inputs from 14 people with 3 different images
for i in range(14):
    for j in range(3):
        filename = str(i) + "_" + str(j) + ".JPG"
        img = cv2.imread(os.path.join(imagePath, filename))

        if img is not None:
            # use color value average, its standard deviation and
            # six different areas from image as inputs
            avg = np.mean(img)
            std = np.std(img)
            avg50 = np.mean(img[50:75, 50:200])
            avg75 = np.mean(img[75:100, 50:200])
            avg100 = np.mean(img[100:125, 50:200])
            avg125 = np.mean(img[125:150, 50:200])
            avg150 = np.mean(img[150:175, 50:200])
            avg175 = np.mean(img[175:200, 50:200])

            input = [avg, std, avg50, avg75, avg100, avg125, avg150, avg175]
            inputs.append(input)

            # use person id as a target
            targets.append(i)

print "inputs:", inputs
print "targets:", targets

# estimation instance
estimation = Estimation()
# use feed forward multilayer perceptron (newff) to train the network
estimation.estimateNEWFF(inputs, targets)

# start video capturing
print "video capturing is starting..."
video_capture = cv2.VideoCapture(0)
while True:
    ret, frame = video_capture.read()
    # gray scale image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect faces
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )

    if len(faces):
        try:
            # find the biggest face in face list
            face = faces[max(enumerate([x[3] for x in faces]), key=operator.itemgetter(1))[0]]

            # coordinates and width-hight values of face
            x, y, w, h = face

            # crop and show the face from (256x256)
            centerX = x+w/2
            centerY = y+h/2
            crop_img = frame[centerY-(height/2):centerY+(height/2), centerX-(width/2):centerX+(width/2)]

            crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

            # prepare input for estimation
            avgFace = np.mean(crop_img)
            stdFace = np.std(crop_img)
            avgFace50 = np.mean(img[50:75, 50:200])
            avgFace75 = np.mean(img[75:100, 50:200])
            avgFace100 = np.mean(img[100:125, 50:200])
            avgFace125 = np.mean(img[125:150, 50:200])
            avgFace150 = np.mean(img[150:175, 50:200])
            avgFace175 = np.mean(img[175:200, 50:200])

            input = [avgFace, stdFace, avgFace50, avgFace75, avgFace100, avgFace125, avgFace150, avgFace175]

            # estimate the class
            result = estimation.activate(input)
            print "class:", result

            # if the class is more than 12 it remembers me
            if result > 12:
                cv2.putText(crop_img, "Welcome My Friend", (5, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 150, thickness=2)
            cv2.imshow("Welcome", crop_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except:
            pass

# when everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
