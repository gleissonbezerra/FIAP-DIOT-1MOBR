from threading import Thread
import smbus2
import time
import json

class I2CManager:
	def __init__(self, busNumber, address, data_event):

		self.bus = None
		self.busNumber = busNumber
		self.address = address
		self.stopped = False

		self.temperature = 0
		self.humidity = 0

		self.data_event = data_event

		print("Starting Serial BUS {} at {}".format(self.busNumber, self.address))

		if self.bus == None:
			self.bus = smbus2.SMBus(self.busNumber)
			time.sleep(1)
		
		print("Serial BUS started!")

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	# def isBusy(self):
	# 	return not self.ack

	def update(self):


		while True:
			if self.stopped:
				return
				
			try:

				data = bytes(self.bus.read_i2c_block_data(self.address, 0, 32)).decode('cp855').rstrip()

				if len(data) > 0:

					print("Received data from I2C slave")
					print(data)

					jsonData = json.loads(data)

					if jsonData != None and "t" in jsonData and "h" in jsonData:

						self.temperature = jsonData["t"]
						self.humidity = jsonData["h"]

						self.data_event()

					else:

						print("Error in get sensor data over i2C ")


			except Exception as e:

				print("I2C Manager communication error on receiving %s " % e)

				time.sleep(1)

				self.bus = None
				self.stopped = False
				self.temperature = 0
				self.humidity = 0

				print("Starting Serial BUS {} at {}".format(self.busNumber, self.address))

				if self.bus == None:
					self.bus = smbus2.SMBus(self.busNumber)
					time.sleep(1)
				
				print("Serial BUS started!")

			time.sleep(0.5)


	def send(self, command):

		try:
			if self.bus != None:
				self.bus.write_i2c_block_data(self.address, 0, command.encode('utf-8'))			
			else:
				print("Serial not ready!")
		except Exception as e:

			print("I2C Manager communication error on sending %s " % e)

			time.sleep(1)

			self.bus = None
			self.stopped = False
			# self.lastData = ""
			# self.ack = False

			print("Starting Serial BUS {} at {}".format(self.busNumber, self.address))

			if self.bus == None:
				self.bus = smbus2.SMBus(self.busNumber)
				time.sleep(1)
			
			print("Serial BUS started!")

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True        

