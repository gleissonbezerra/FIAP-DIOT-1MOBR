import cv2

import numpy as np
import time


class InferenceCapture():

    def __init__(self):

        # self.threshold = 0.2
        self.confidenceLevel = 0.50

        # initialize the list of class labels MobileNet SSD was trained to detect
        self.CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
            "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
            "sofa", "train", "tvmonitor"]

        # load our serialized model from disk
        print("[INFO] loading model...")
        self.NET = cv2.dnn.readNetFromCaffe(r'mobilenet/MobileNetSSD_deploy.prototxt', r'mobilenet/MobileNetSSD_deploy.caffemodel')

        
    def inference(self, frame):

        # Get current time before we capture a frame
        tFrameStart = time.time()

        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        self.NET.setInput(blob)
        detections = self.NET.forward()

        jsonArray = [] #detections

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > self.confidenceLevel:

                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")

                jsonData = \
                {
                "label": self.CLASSES[idx],
                "score": round(float(confidence),4),
                "bbox": {"x1": int(x1),"y1": int(y1),"x2": int(x2),"y2": int(y2)}
                }                

                jsonArray.append(jsonData)


        #update the FPS counter
        timeElapsedInMs = (time.time() - tFrameStart) * 1000
        fps = 1000.0 / timeElapsedInMs

        jsonFinal = {"fps": round(fps,1)}

        jsonFinal.update({"detections": jsonArray})

        return (jsonFinal)

