#-------------------------------------------
#
#    ESP32 WiFi Camera (OV7670 FIFO Version)
#    ESP32WiFiCAM-OV7670
#
#    file:main.py  
# 
#

from ESP32WiFiCAMRAW import ESP32WiFiCAMRAW

camera = ESP32WiFiCAMRAW()

if camera.setup():
    camera.mainLoop()
else:
    print("Error in setup CameraSystem")


"""
  *** test pattern ***
  before test, comment out setup() and cameraMainLoop()

#-------------------------------
#test_1 SD FileSystem Test
#-------------------------------
import ESP32WiFiCAMRAW
ESP32WiFiCAMRAW.SD_setup()
from upysh import *
ls('/sd')

#-------------------------------
#test_2 file Upload Test
#-------------------------------
import ESP32WiFiCAMRAW
ESP32WiFiCAMRAW.setup()
url=ESP32WiFiCAMRAW.AWSAPIURL
key=ESP32WiFiCAMRAW.AWSAPIKEY
file='/sd/DCIM/201910/191013_1151.raw'
ESP32WiFiCAMRAW.uploadFile(file,url,key)

# if OK; then return 200
# (200, '<html><body>OK</body></html>')

"""
