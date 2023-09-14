from flask import Flask, render_template, Response, request

from InferenceCapture import InferenceCapture

import numpy as np

import sys
import json
import cv2


app = Flask(__name__)

lastFrame = None
lastInference = None



def parseRequest(r):

    # check if the post request has the file part
    frame = None
   
    if 'frame' in r.files:

        frameFile = r.files['frame']

        if frameFile:
            jpg = frameFile.read()
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

   
    return frame


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


@app.route('/analyze',methods=['POST'])
def analyze():
    global lastFrame
    global lastdFrame
    global lastInference
    global ic

    if request.method == 'POST':

        f = parseRequest(request)

        r = ic.inference(f)

        lastFrame = f
        lastInference = r

        return Response(json.dumps(r), status=201, mimetype='application/json') #return json

    else:
        return Response("Invalid method")



@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def gen_frames():  # generate frame by frame from camera
    global lastFrame
    global lastInference

    fps = 0

    while True:

        try:

            f = lastFrame
            m = lastInference

            if m != None and m != [] and "detections" in m:
                
                fps = m["fps"]
                d = m["detections"]

                for i in d:
                    #print(i["name"])
                    x1 = i["bbox"]["x1"]
                    y1 = i["bbox"]["y1"]
                    x2 = i["bbox"]["x2"]
                    y2 = i["bbox"]["y2"]

                    cv2.rectangle(f, (x1, y1), (x2, y2), (0,255,0), 2)
                    text = "{}: {:.2f}%".format(i["label"], i["score"]*100)

                    cv2.putText(f, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)


            cv2.putText(f, "FPS: {:.2f}".format(fps), (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

            encodedFrame = cv2.imencode( '.jpg', f)
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + encodedFrame[1].tobytes() + b'\r\n\r\n')

        except:
            print("Error on enconding frame bytes!")
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n\r\n')

def main():

    global ic

    try:
        print("\nPython %s\n" % sys.version )
        print("MobileNet Module." )

        ic = InferenceCapture()

        app.run(host='0.0.0.0', port=8080)

    except KeyboardInterrupt:
        print("MobileNet Module stopped" )


if __name__ == '__main__':

    main()



