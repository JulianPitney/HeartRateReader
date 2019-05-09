import serial
from multiprocessing import Process
import time
import binascii
from time import sleep

SAMPLE_RATE = 1


class Packet:
	
	def __init__(self, data, packetType):
		
		self.packetType = packetType
		self.data = data

	

def read_packet(HRSerInterface):

	while(1):

		if(HRSerInterface.read() == b'\xff'):
		
			keyByte = HRSerInterface.read()	
			paramCodeStart = HRSerInterface.read()
			paramVal = HRSerInterface.read(1)
			paramCodeEnd = HRSerInterface.read()
			
			if(paramCodeStart == b'\xf4'):
				return Packet(str(int.from_bytes(paramVal, byteorder='little')), 4)
			if(paramCodeStart == b'\xf5'):
				return Packet(str(int.from_bytes(paramVal, byteorder='little')), 5)
			if(paramCodeStart == b'\xf6'):
				return Packet(str(int.from_bytes(paramVal, byteorder='little')), 6)
			if(paramCodeStart == b'\xf7'):
				return Packet(str(int.from_bytes(paramVal, byteorder='little')), 7)	


def monitor_stream(deviceNum):
	
	startTime = time.time()
	
	try:
		hrSerInterface = serial.Serial("/dev/ttyUSB" + str(deviceNum))
	except:
		print("Unable to open /dev/ttyUSB" + str(deviceNum))
		return -1

	try:
		hrCsv = open("hr" + str(deviceNum) + ".csv", 'w')
	except:
		print("Unable to open hr" + str(deviceNum) + ".csv!")
		return -1

	sampleTimer = time.time()
	
	while(1):
		
		currentTime = time.time()

		if (currentTime - sampleTimer < SAMPLE_RATE):

			read_packet(hrSerInterface)
		else:
			
			hrHundredsData = None
			hrHundredsReceived = False				
			hrTensData = None
			hrTensReceived = False		
			spO2Data = None
			spO2Received = False		
			plethysmogramData = None
			plethysmogramReceived = False
	
			while(not hrHundredsReceived or not hrTensReceived or not spO2Received or not plethysmogramReceived):
			
				packet = read_packet(hrSerInterface)			

				if (packet.packetType == 4):
					hrHundredsData = packet.data
					hrHundredsReceived = True
				elif (packet.packetType == 5):
					hrTensData = packet.data
					hrTensReceived = True
				elif (packet.packetType == 6):
					spO2Data = packet.data
					spO2Received = True
				elif (packet.packetType == 7):
					plethysmogramData = packet.data
					plethysmogramReceived = True

			combinedHR = int(hrHundredsData) * 100
			combinedHR += int(hrTensData)
			csvLine = str(combinedHR) + "," + spO2Data + "," + plethysmogramData + "," + str(currentTime - startTime) + "\n"
			hrCsv.write(csvLine)
			print("Monitor" + str(deviceNum) + ": " + csvLine)
			sampleTimer = time.time()
				




hr0Proc = Process(target=monitor_stream, args=(0,))
hr1Proc = Process(target=monitor_stream, args=(1,))
hr2Proc = Process(target=monitor_stream, args=(2,))
hr3Proc = Process(target=monitor_stream, args=(3,))

hr0Proc.start()
hr1Proc.start()
hr2Proc.start()
hr3Proc.start()

sleep(10)








