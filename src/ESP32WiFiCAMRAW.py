#-------------------------------------------
#
#    ESP32 WiFi Camera (OV7670 FIFO Version)
#    ESP32WiFiCAM-OV7670
#
#    file:ESP32WiFiCAMRAW.py
#   

import uos, utime
from upysh import *
from machine import SPI, Pin
from sdcard import SDCard
from ST7735 import TFT
from terminalfont import terminalfont
from PhotoUploaderAWS import uploadFileAWS
from OV7670 import OV7670, QQVGASIZE, RGB565BPP
import mylib

ESPCAM_VERSION = "ESP7670CAM_RAW(V0.02)"


#
# AWS Web API Parameters (RAW Image Converter Service)
#
AWSAPIURL="https://foo.amazonaws.com/test/yourFunc"  # set your Web API URL
AWSAPIKEY='setYourAPIKey'                            # set your Web API KEY

#
# WiFi Connection Parameters
#
SSID = 'ssidXXXXX'   # set SSID for connect WiFi Network
PASS = 'passXXXXX'   # set password  for connect WiFi Network

#
# define for SPI Speed
#
HSPI_BAUDRATE=20000000    # TFT/FIFO Control 20MHz
VSPI_BAUDRATE=32000000    # SD Control 32MHz


#-----------------------------
#
# PIN ASSIGN
#

# for I2C
I2C_SCL = 32
I2C_SDA = 33

# for SD 
SD_SPI_SCK = 18
SD_SPI_MOSI = 23
SD_SPI_MISO = 19
SD_CS  =  5

# for TFT
TFT_SPI_SCK = 14
TFT_SPI_MOSI = 13
TFT_SPI_MISO = 12
TFT_DC = 4
TFT_RESET = 16
TFT_CS = 27

# for FIFO Control
FIFO_VSYNC = 39
FIFO_RDCLK = 0
FIFO_WE = 26
FIFO_RRST = 21
FIFO_WRST = 22
FIFO_PL = 25

# for ShutterButton
SHUTTER_BUTTON = 36


#----------------------------------
#  
#   ESP32 WiFi Camera Class 
#   ESP32WiFiCAM
#  
#  
class ESP32WiFiCAMRAW():
    """ESP32 WiFi Camera Class"""
    
    def __init__(self):

        #
        # var for instance of HSPI(for TFT and FIFO), TFT
        #
        self.hspi = None
        self.vspi = None
        self.tft = None
        self.sd = None
        
        #
        # flags for setup status
        #
        self.stat_if = None     # status for NetworkInterface
        self.stat_ntp = None    # status for NTP
        self.stat_ov7670 = None # status for OV7670
        self.stat_sd = None     # status for SD
        
        # var for instance of shutterButton
        self.shutter = None

        #
        # flag for shutter pressed
        #
        self.shutterPressed = False

        # var for instance of ImageSensor(OV7670)
        self.ov7670 = None
    

    def setup(self):

        mylib.collectMemory()
    
        # SPI FOR TFT/OV7670 FIFO
        self.hspi = SPI(1, baudrate=HSPI_BAUDRATE, polarity=0, phase=0, sck=Pin(TFT_SPI_SCK), mosi=Pin(TFT_SPI_MOSI), miso=Pin(TFT_SPI_MISO))
        #
        # setup TFT Unit
        #
        self.tft = self.TFT_setup(self.hspi, TFT_DC, TFT_RESET, TFT_CS)
    
        #
        # SPI FOR SD Card
        #
        self.vspi = SPI(2, baudrate=VSPI_BAUDRATE, polarity=1, phase=0, sck=Pin(SD_SPI_SCK), mosi=Pin(SD_SPI_MOSI), miso=Pin(SD_SPI_MISO))
        #
        # setup SD Unit
        #
        self.sd = self.SD_setup(self.vspi, SD_CS)
        if self.sd is None:
            self.stat_sd = False
        else:
            self.stat_sd = True
    
        mylib.wlan_connect(SSID, PASS)   
        self.stat_ntp = mylib.ntp_setup()
        mylib.collectMemory()
        if self.stat_sd and self.stat_ntp:
            mylib.setupSDFileSystem(self.sd)
        else:
            print("Initialization failed, so skip setupSDFileSystem()")
        mylib.collectMemory()
    
        #
        # setup ImageSensor(OV7670) Unit
        #
        self.ov7670 = OV7670(I2C_SCL, I2C_SDA)
        self.stat_ov7670 = self.ov7670.getStatus()

        # setup FIFO
        if self.stat_ov7670:
             self.ov7670.setupFIFO(self.hspi, FIFO_VSYNC, FIFO_RDCLK, FIFO_WE, FIFO_RRST, FIFO_WRST, FIFO_PL)

        # setup shutter button and IRQ
        self.shutter = Pin(SHUTTER_BUTTON, Pin.IN)  # 36 is assigned for ShutterButton
        self.shutter.irq(trigger=Pin.IRQ_FALLING, handler=self.cb_shutterPressed)
 
        return self.stat_sd and self.stat_ntp and self.stat_ov7670

    #
    # call back function for ShutterButton
    #
    def cb_shutterPressed(self, p):
        self.shutterPressed = True
        print("ShutterButton Pressed:", self.shutterPressed)

    
    #
    # main loop for ESPWiFiCAM(RAW)
    #
    def mainLoop(self):
    
        self.tft.fill(self.tft.BLACK)
        self.shutterPressed = False
        while True:
            print("-------------")
            self.ov7670.takePicture()
            self.showQQVGAPicture()
            if self.shutterPressed:
                self.tft.text((10, 120), "!! Shutter Pressed !!", self.tft.RED, terminalfont)
                self.tft.text((11, 120), "!! Shutter Pressed !!", self.tft.PURPLE, terminalfont)
                self.ov7670.setVGABayerMode()      # change to VGA_RAW Mode
                self.takePictureAndUpload()        # 
                self.shutterPressed = False        # clear flag
                self.ov7670.setQQVGARGB565Mode()   # change to QQVGA_RGB565
                self.tft.fillrect((0, 120), (160, 128), self.tft.BLACK)
            print(mylib.collectMemory())
    
    def takePictureAndUpload(self):

        fileName = None
        saveState = None

        mylib.collectMemory()
        self.ov7670.takePicture()        
        fileName = mylib.getPhotoFileNameWithPath('raw')
        saveState = self.ov7670.saveVGARawPicture(fileName)
        if saveState:
            print("OK! save done")
        else:
            print("Error in save Picture")

        mylib.collectMemory()
        if saveState:
            print("send to AWS:{:s}".format(AWSAPIURL))
            print("file:{:s}".format(fileName))
            s = utime.ticks_ms()
            (status, info) = uploadFileAWS(fileName, AWSAPIURL, AWSAPIKEY)
            e = utime.ticks_ms()
            if status == 200:
                print("OK! send to AWS done", status)
            else:
                print("Error! send to AWS in fail", status)
            print("upload time:{:d}(ms)".format(utime.ticks_diff(e, s)))
        mylib.collectMemory()
    
    def showQQVGAPicture(self,screenClear=False, drawLines=1):
      
        (h_size, v_size) = QQVGASIZE
        s = utime.ticks_ms()
        if screenClear:
            self.tft.fill(self.tft.BLACK)
        mylib.collectMemory()
        print("free mem: ", end="")
        print(mylib.reportMemory())
        rectSize = h_size * RGB565BPP * drawLines 
        lineBuf=bytearray(rectSize)
        self.ov7670.FIFOReadReset()   # read data from Top of FIFO
        for y in range(0, v_size, drawLines):
            if self.shutterPressed:
                print("shutter pressed, so stop drawing")
                break
            self.ov7670.getPixelFromFIFO(lineBuf, rectSize, False)
            self.tft.image(0, y, h_size - 1, y + drawLines, lineBuf)
        e = utime.ticks_ms()
        print("Preview draw time:{:d}(ms)".format(utime.ticks_diff(e, s)))
        mylib.collectMemory()
    

    #---------------------------------------------
    #
    # Devie Setup (TFT, SD)
    #

    def TFT_setup(self, spi, dc, reset, cs):
    
        # setup TFT
        tft = TFT(spi=spi, aDC=dc, aReset=reset, aCS=cs)
        tft.initr()
        tft.rgb(True)
        tft.rotation(3)
        tft.fill(tft.BLACK)
        tft.text((0, 0), ESPCAM_VERSION, tft.WHITE, terminalfont)
        return tft
    
    def SD_setup(self, spi, cs):
    
        sd = None

        # setup SD card
        try:
            sd = SDCard(spi, Pin(cs))
        except Exception as e:
            print("Error in SDCard()!!")
            print(e)
            return None
        else:
            print("SD OK")
    
        # mount sd volume
        utime.sleep(0.1)
        uos.mount(sd, '/sd')
        utime.sleep(0.1)
        uos.listdir('/sd')
        utime.sleep(0.1)
        ls('/sd')
        return sd



#
# end of code
#