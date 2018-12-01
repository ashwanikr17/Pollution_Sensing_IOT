Step 1: Installation of Raspbian on 16 GB (preferred) SD card:

			Download and Extract Raspbian Stretch for desktop zip from( https://www.raspberrypi.org/downloads/raspbian/ )
			
			Download and Install Win32 Disk Imager from (https://sourceforge.net/projects/win32diskimager/) to burn the Raspbian OS onto SD card
			
			Open Win32 DI -> Browse -> Select the image raspbian stretch -> Write -> Yes
			

Step 2: Insert the card in RPi and power it up (5v DC)


Step 3: Preferences -> Rpi Configuration -> Localisation -> Set Locale (Country to India), Timezone (Area to Indian and Location to Maldives), Keyboard (Country to India and Variant to English(India with rupee)), Wifi country (India) -> Ok -> Yes to Reboot


Step 4: Connect to the wifi


Step 5: Go to Preferences -> RPi Configuration -> Interfaces -> Enable all -> Reboot


Step 6: Downloading all the required libraries:

			Open Terminal:
			
				$ sudo apt-get update
				
				$ sudo apt-get upgrade
				
				
			For pi camera library:
				$ sudo apt-get install python-picamera
				
			For arduino:
				Upload the code in Arduino IDE to arduino board using FTDI cable and open serial 
				monitor to verify output.
				
				
			For conversion of image to text and compression:
				$ sudo apt-get install zlib1g-dev
				$ sudo apt-get install python3-pip
				$ sudo apt-get install python-pip
				$ sudo pip3 install pybase64
			
			For firebase-admin:
				$ sudo pip install requests
				$ sudo pip install firebase-admin
				$ sudo pip install --upgrade google-auth-oauthlib
			

Step 7: Download the source code:

			Open Terminal $ git clone https://github.com/ashwanikr17/Pollution_Sensing_IOT.git
			


Step 8: To run the program:

		$ sudo python sensor_polling_*.py
			
			
		
