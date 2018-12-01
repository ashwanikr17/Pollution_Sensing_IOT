import sys
import os
# from gps import *
import time
from datetime import datetime
# import IMU
import zlib
import firebase_admin
from firebase_admin import credentials,firestore
import multiprocessing as mp
from picamera import PiCamera
import urllib2
# from threading import Thread, Event
import requests
import errno
from socket import error as SocketError
import difflib
# import pigpio
import serial
# rx=26

polfile = ''
arduinofile = ''
gpsfile = ''
imagefile = ''
bmefile = ''



gpsfile_limit = 2000
polfile_limit = 2000
bmefile_limit = 2000
arduinofile_limit = 2000
imagefile_limit = 4



gpsfile_lines = gpsfile_limit 
polfile_lines = polfile_limit
bmefile_lines = bmefile_limit
arduinofile_lines = arduinofile_limit
imagefile_lines = imagefile_limit

address_prefix =''          #'/home/pi/Documents/LOG/'


try:
    import struct
except ImportError:
    import ustruct as struct
    
# pi=pigpio.pi()
# if not pi.connected:
#     exit(0)
    
#pi.set_mode(rx,pigpio.INPUT)
# pi.bb_serial_read_open(rx,9600,8)
# dbuffer=[]
 
#stop_event = Event()
#when internet is not connected it will retry sending data

def process_directory(localdir,db):
	flist = os.listdir(localdir)
	print ("No of files in {} = {}".format(localdir,len(flist)))
	if (len(flist)>2):
		for localfile in flist[1:-1]:				#0th file in .keep , last file is currently in use
			# print ("Processing file {}".format(localfile))
			if(localfile[-3:] != 'txt'):		#to skip the occasional img.jpg  file which can be present in file list
				continue
			f = open(localdir+'/'+localfile,'r')
			# print ("Opened file {}".format(localfile))
			lines=f.read().split('@')[1:]
			f.close()
			# print ( "Read {} lines in {}".format(len(lines),localdir))
			dic = {}
			# if (len(lines)>data_lines_uploaded):
			for line in lines:
				linelist = line.split(',')
				ltime = linelist[0]
				dic[unicode(ltime,'utf-8')] = unicode(linelist[1],'utf-8')

			# print ("######################Dictionary made!")
			# print(str(dic))
			if (len(dic)>0):
				doc_ref = db.collection(localdir).document(localfile)
				doc_ref.set(dic)    
				print( "#####################Updated {} to firebase".format(localdir))    
				#os.system('cp '+localdir+'/'+localfile+' backup/'+localdir+'/')
				os.unlink(localdir+'/'+localfile)

def write_to_firebase(db):
	global address_prefix
	retry_on = (requests.exceptions.Timeout,requests.exceptions.ConnectionError,requests.exceptions.HTTPError,IOError)
	time_out=1
	# time_sleep = 100
	# print ("Started process write to firebase")
	while True:
		if (not internet_on()):
			time.sleep(time_out)
			continue
		try:
			# print("Trying to update to firebase")
			# process_directory(u'gps',db)
			process_directory(u'image',db)
			process_directory(u'poldata',db)
			process_directory(u'arduino',db)
			process_directory(u'bme',db)
			time.sleep(time_out)
		except IOError ,e :
			print("Error opening file: {}".format(str(e)))
			time.sleep(time_out)
		except Exception, e:
			print('Error {} : {}'.format(type(e).__name__,e.message))
			# print(e.message)
			pass
		finally:
			time.sleep(time_out)
          

#checks it internet connection is available
def internet_on():
	exc = (urllib2.URLError, urllib2.HTTPError)
	try:
		urllib2.urlopen('http://216.58.192.142',timeout=3)
		# print("Internet connection present")
		return True
	except exc:		
		# print("Internet connection not present")	
		return False
	# except socket.timeout:
	# 	# print("Internet connection not present")
	# 	return False
	except SocketError as e:
		# if e.errno !=errno.ECONNRESET:
		    #print(3)
		    # raise
		pass

# thread to take accelerometer readings and writing it in a file and firebase
def writearduino(ser):
	global address_prefix,arduinofile,arduinofile_lines,arduinofile_limit
	tlast = datetime.utcnow()
	while True:
		if ( arduinofile_lines >= arduinofile_limit):
			ltime=str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3])
			arduinofile = 'arduino/'+ltime+ 'arduino.txt'
			arduinofile_lines = 0
		# string = address_prefix+'accel.txt'
		#acc='/accel/acc%s'%local
		
		#collecting the value of accelerometer every 16 msec
		read_serial = ser.readline().strip()
		# print("Read: {}".format(read_serial))
		if (len(read_serial)<10):
			continue
		if(read_serial[0:3] == 'PMS' ):
			writepol(read_serial)
			continue
		if(read_serial[0:3] == 'BME' ):
			writebme(read_serial)
			continue
		if(read_serial[0] != 'E' ):
			continue
		ltime=str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3])
		s=("@%s,%s\n"%(ltime,read_serial)) 
		fa=open(address_prefix+arduinofile,"a+")
		fa.write(s)
		fa.close()
		arduinofile_lines+=1
		print ("Wrote from arduino")
		tnow = datetime.utcnow()
		delta = (tnow-tlast).total_seconds()+(tnow-tlast).microseconds/1000000.0
		if (delta< 0.035):
			time.sleep(0.035-delta)
		tlast = datetime.utcnow()

# def writegps():
# 	global address_prefix,gpsfile,gpsfile_limit,gpsfile_lines
# 	while True:
# 		if ( gpsfile_lines >= gpsfile_limit):
# 			ltime=str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
# 			gpsfile = 'gps/'+ltime+ 'gps.txt'
# 			gpsfile_lines = 0
# 		localtime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
# 		print(('latitude    ' , gpsd.fix.latitude))
# 		print(('longitude   ' , gpsd.fix.longitude))
# 		print(('Time        ' , localtime))

# 		data="%s\t,Lat:%f\tLong:%f" %(localtime,gpsd.fix.latitude,gpsd.fix.longitude) 
# 		f=open(address_prefix+gpsfile,"a+")
# 		f.write("%s\n" %data)  
# 		f.close()
# 		gpsfile_lines+=1
# 		time.sleep(10)  
def writeimage():
	global address_prefix,imagefile,imagefile_lines,imagefile_limit
	tlast = datetime.utcnow()
	while True:
		if ( imagefile_lines >= imagefile_limit):
			ltime=str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3])
			imagefile = 'image/'+ltime+ 'image.txt'
			imagefile_lines = 0
		localtime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
		# print(('Time        ' , localtime))
		string1 = address_prefix+'image/img.jpg'
		camera=PiCamera()
		camera.capture(string1)
		camera.close()
		# time.sleep(0.5)
		# print(string1)
		imag=string1
		#encoding jpeg to text and compressing the text
		with open(imag,"rb") as imageFile:
			image_64= zlib.compress(imageFile.read()).encode('base64')
		#delete image file
		data="@%s,%s\n" %(localtime,image_64) 
		f=open(imagefile,"a+")
		f.write(data)  
		f.close()   
		imagefile_lines+=1
		print("Wrote an image line!")
		os.unlink(string1)
		tnow = datetime.utcnow()
		delta = (tnow-tlast).total_seconds()+(tnow-tlast).microseconds/1000000.0
		if (delta < 2.0):
			time.sleep(2.0-delta)
		tlast = datetime.utcnow()
def writepol(pol_data):
	global address_prefix,polfile,polfile_limit,polfile_lines
	
	if ( polfile_lines >= polfile_limit):
		ltime=str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3])
		polfile = 'poldata/'+ltime+ 'pol.txt'
		polfile_lines = 0
	localtime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]

	data="@%s\t,%s" %(localtime,pol_data) 
	f=open(address_prefix+polfile,"a+")
	f.write("%s\n" %data)  
	f.close()
	polfile_lines+=1
	print ("Wrote a poldata line!")
	return	
def writebme(bme_data):
	global address_prefix,bmefile,bmefile_limit,bmefile_lines
	
	if ( bmefile_lines >= bmefile_limit):
		ltime=str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3])
		bmefile = 'bme/'+ltime+ 'bme.txt'
		bmefile_lines = 0
	localtime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]

	data="@%s\t,%s" %(localtime,bme_data) 
	f=open(address_prefix+bmefile,"a+")
	f.write("%s\n" %data)  
	f.close()
	bmefile_lines+=1
	print ("Wrote a bmedata line!")
	return	
		

cred = credentials.Certificate("serviceAccountKey2.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
# gps_file_ref = db.collection(u'gps').document(u'gps')
# arduino_file_ref = db.collection(u'sensor_data_mt').document(u'arduino')
# polfile_ref = db.collection(u'sensor_data_mt').document(u'poldata')
# image_file_ref = db.collection(u'sensor_data_mt').document(u'image')
# bme_file_ref = db.collection(u'sensor_data_mt').document(u'bme')
# gps_file_ref.set({})
# arduino_file_ref.set({})
# polfile_ref.set({})
# image_file_ref.set({})
# bme_file_ref.set({})
os.system('clear')


# class GpsPoller(threading.Thread):
#   def __init__(self):
#     threading.Thread.__init__(self)
#     global gpsd
#     gpsd = gps(mode=WATCH_ENABLE) 
#     self.current_value = None
#     self.running = True
 
#   def run(self):
#     global gpsd
#     while gpsp.running:
#       next(gpsd) 
# if __name__ == '__main__':
#   gpsp = GpsPoller() 
#   gpsp.start()
# count=0


ser = serial.Serial('/dev/ttyUSB0',9600)
accel_p = mp.Process(target=writearduino,args=(ser,))
accel_p.start()
#   gps_p = mp.Process(target=writegps)
#   gps_p.start()
#   pol_p = mp.Process(target=writepol)
#   pol_p.start()
image_p = mp.Process(target=writeimage)
image_p.start()

write_to_firebase(db)

# action_thread_1=Thread(target=accel,args=())
# action_thread_1.start()

# writeLog(logfile)
# f.close()
