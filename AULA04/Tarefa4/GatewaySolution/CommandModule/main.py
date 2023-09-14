from flask import Flask, Response, request

from BlynkConnection import BlynkConnection
from I2CManager import I2CManager

import json
import sys
import os
import time

app = Flask(__name__)


def dataHandler():
    global i2c
    global blynkC

    blynkC.blynk.virtual_write(0, i2c.temperature)
    blynkC.blynk.virtual_write(1, i2c.humidity)

def parseRequest(r):
 
    return r.json

@app.route('/alert',methods=['POST'])
def alert():

    global i2c
    global blynkC
    global I2C_SLAVE_ADDRESS
    global alertStarted
    global alertTimer

    if request.method == 'POST':

        jsonData = parseRequest(request)

        print("Received event data: "+json.dumps(jsonData))

        #check if people is present for a while
        if jsonData != None and "detections" in jsonData:

            peopleDetected = 0

            for object in jsonData["detections"]:

                if object["label"] == "person":
                    peopleDetected += 1

            if peopleDetected > 0:
                if alertStarted:

                    PEOPLE_ALERT_INTERVAL = float(os.getenv('PEOPLE_ALERT_INTERVAL', "5.00"))

                    if time.time() - alertTimer >= PEOPLE_ALERT_INTERVAL:
                        print ("Alert confirmed. Sendindg notification...")


                        blynkC.log_event("people_alert")

                        print ("Notification sent!")

                        #send close command over i2c
                        command = "close"
                        print("Sending "+command+" to I2C slave!")
                        i2c.send(command)			

                        alertStarted = False

                    else:
                        print ("Trying to confirm people alert...")
                else:
                    print ("Starting people alert timer..")
                    alertStarted = True
                    alertTimer = time.time()
            else:
                alertStarted = False
                print ("Finished or False Alert!")


        return Response("ok", status=201) 

    else:
        return Response("Invalid method")


def main():

    global i2c
    global blynkC
    global I2C_BUS_NUMBER
    global I2C_SLAVE_ADDRESS
    global alertStarted
    global alertTimer
    
    alertStarted = False
    alertTimer = time.time()

    I2C_BUS_NUMBER = int(os.getenv('I2C_BUS_NUMBER', "1"))
    I2C_SLAVE_ADDRESS = int(os.getenv('I2C_SLAVE_ADDRESS', 0x08))

    BLYNK_TOKEN = os.getenv('BLYNK_TOKEN', "")

    blynkC = BlynkConnection(BLYNK_TOKEN).start()
    i2c = I2CManager(I2C_BUS_NUMBER, I2C_SLAVE_ADDRESS, dataHandler).start()

    try:
        print("\nPython %s\n" % sys.version )
        print("Command Module." )

        app.run(host='0.0.0.0', port=8081)

    except KeyboardInterrupt:
        print("Command Module stopped" )


if __name__ == '__main__':

    main()



