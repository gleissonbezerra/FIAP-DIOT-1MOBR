# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import cv2 as cv
import requests
import os
import uuid
import json

import asyncio
import sys
import signal
import threading



# Event indicating client stop
stop_event = threading.Event()

def resize(img, scale_percent):

    width = int(img.shape[1] * scale_percent)
    height = int(img.shape[0] * scale_percent)

    dim = (width, height)

    return cv.resize(img, dim, interpolation = cv.INTER_AREA)


def processFrame(frameBytes):
    global INFERENCE_URL

    multipart_form_data = {'frame': ("frame.jpg", frameBytes)}

    response = requests.post(INFERENCE_URL,files=multipart_form_data, timeout=2)

    return response.json()

async def run_sample():
    # Customize this coroutine to do whatever tasks the module initiates
    # e.g. sending messages
    global vf
    global ALERT_URL

    INFERENCE_INTERVAL = float(os.getenv('INFERENCE_INTERVAL', "1.0"))


    while True:

       
        (ret, frame) = vf.read()

        if not ret:
            print("No frame data!!!")
            continue

        frame = resize(frame, 0.5)

        frameBytes = cv.imencode( '.jpg', frame)[1].tobytes()
        r = processFrame(frameBytes)

        print (r)

        if r != None and "detections" in r:

            try:
                print("Posting detections as event..")
                requests.post(ALERT_URL,json=r, timeout=2)
                print("Event done!")

            except:
                print("Error on posting detections!")

        await asyncio.sleep(INFERENCE_INTERVAL)


def main():
    global vf
    global INFERENCE_URL
    global ALERT_URL

    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "Camera Module for Python" )

    print("Python3 cv2 version: %s" % cv.__version__)

    CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', "0"))
    CAMERA_INTERVAL = float(os.getenv('CAMERA_INTERVAL', "1.0"))
    INFERENCE_URL = os.getenv('INFERENCE_URL', "http://0.0.0.0:8080/analyze")
    ALERT_URL = os.getenv('ALERT_URL', "http://0.0.0.0:8080/alert")

    vf = cv.VideoCapture(CAMERA_INDEX)

    if not vf.isOpened():
        print("Error opening camera!!!")
        exit()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("Camera Module stopped!")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_sample())
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down Camera Modulre...")
        vf.release()
        loop.close()


if __name__ == "__main__":
    main()
