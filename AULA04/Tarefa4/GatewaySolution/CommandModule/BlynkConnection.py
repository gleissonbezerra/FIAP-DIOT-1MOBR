from threading import Thread
import time

import BlynkLib

class BlynkConnection:
	def __init__(self, token):

		self.stopped = False

		self.blynk = BlynkLib.Blynk(token, server="blynk.cloud", port=80)

		print("Blynk connection started!")

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	# def isBusy(self):
	# 	return not self.ack

	def update(self):


		while True:
			if self.stopped:
				return
				
			self.blynk.run()



	def send(self, data_stream, value):

			
		print("Sending data to blynk...")

		self.blynk.virtual_write(data_stream, value)

		print("Data sent!")


	def log_event(self, value):

			
		print("Sending alert to blynk...")

		self.blynk.log_event(value)

		print("Alert sent!")

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True        

