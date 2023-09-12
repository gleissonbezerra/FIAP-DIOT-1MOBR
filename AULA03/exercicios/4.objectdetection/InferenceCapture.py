import cv2 as cv

import numpy as np

class InferenceCapture():

    def __init__(self):

        self.threshold = 0.2
        self.confidenceLevel = 0.25
        self.LABELS = []

        print("")

        yolocfg = r'yolo/yolov3-tiny.cfg'
        yoloweight = r'yolo/yolov3-tiny.weights'
        labelsPath = r'yolo/coco-pt.names'

        # load the COCO class labels our YOLO model was trained on
        self.LABELS = open(labelsPath).read().strip().split("\n")

        # derive the paths to the YOLO weights and model configuration
        weightsPath = yoloweight
        configPath = yolocfg

        # load our YOLO object detector trained on COCO dataset (80 classes)
        print("[INFO] loading YOLO from disk...")
        self.net = cv.dnn.readNetFromDarknet(configPath, weightsPath)

        # set CUDA (GPU) as the preferable backend and target
        #print("[INFO] setting preferable backend and target to CUDA...")
        # self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        # self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)

        print("[INFO] determine only the *output* layer names that we need from YOLO...")

        # determine only the *output* layer names that we need from YOLO
        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i - 1] for i in self.net.getUnconnectedOutLayers()]

        print("[INFO] All set!")

        
    def inference(self, frame):

        # initialize the width and height of the frames
        (H, W) = frame.shape[:2]

        # construct a blob from the input frame and then perform a forward
        # pass of the YOLO object detector, giving us our bounding boxes
        # and associated probabilities
        blob = cv.dnn.blobFromImage(frame, 1/255, (416, 416), swapRB=True, crop=False)

        self.net.setInput(blob)

        #print("net forward...")
        layerOutputs = self.net.forward(self.ln)

        # initialize our lists of detected bounding boxes, confidences,
        # and class IDs, respectively
        boxes = []
        confidences = []
        classIDs = []

        jsonArray = [] #detections

        # loop over each of the layer outputs
        for output in layerOutputs:
            # loop over each of the detections
            for detection in output:
                # extract the class ID and confidence (i.e., probability)
                # of the current object detection
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                # filter out weak predictions by ensuring the detected
                # probability is greater than the minimum probability
                if confidence > self.confidenceLevel:
                    # scale the bounding box coordinates back relative to
                    # the size of the image, keeping in mind that YOLO
                    # actually returns the center (x, y)-coordinates of
                    # the bounding box followed by the boxes' width and
                    # height
                    box = detection[0:4] * np.array([W, H, W, H]) 

                    (centerX, centerY, width, height) = box.astype("int")

                    # use the center (x, y)-coordinates to derive the top
                    # and and left corner of the bounding box
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    # update our list of bounding box coordinates,
                    # confidences, and class IDs
                    classIDs.append(classID)
                    confidences.append(float(confidence))
                    
                    boxes.append([x, y, int(width), int(height)])


        # apply non-maxima suppression to suppress weak, overlapping
        # bounding boxes
        idxs = cv.dnn.NMSBoxes(boxes, confidences, self.confidenceLevel, self.threshold)


        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for i in idxs.flatten():

                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                jsonData = \
                {
                "label": self.LABELS[classIDs[i]],
                "score": round(confidences[i],4),
                "bbox": {"x": x,"y": y,"w": w,"h": h}
                }                

                jsonArray.append(jsonData)

        jsonFinal = {"detections": jsonArray}

        return (jsonFinal)
    