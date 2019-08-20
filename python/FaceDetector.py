import cv2
import numpy as np


class FaceDetector:
    def __init__(self,caffe_model_file,prototxt_file,detection_threshold):
        self.caffe_model_file = caffe_model_file
        self.prototxt_file = prototxt_file
        self.detection_threshold = detection_threshold
        self.net = cv2.dnn.readNetFromCaffe(self.prototxt_file,self.caffe_model_file)
        print("[INFO] Caffe model loaded...")
        print("[INFO] Ananymisation algorithm running...")
    
    def recognition(self,frame):
        """
        frame : is the frame where we want to detect the face
        net   : net is the used neural network that we will be using
        """
        h,w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,(300, 300), (104.0, 177.0, 123.0))
        self.net.setInput(blob)
        detections = self.net.forward()

        for i in range(0,detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]
            if confidence > self.detection_threshold:
                print("[FACE DETECTED]confidence:"+str(confidence))
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                rectWidth = abs(startX-endX)
                rectHeight = abs(startY-endY)

                #blurring
                frame[startY:startY+rectHeight, startX:startX+rectWidth] = cv2.GaussianBlur(frame[startY:startY+rectHeight, startX:startX+rectWidth],(0,0),30)

        return frame

