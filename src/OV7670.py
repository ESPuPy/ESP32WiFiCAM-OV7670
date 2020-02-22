#-------------------------------------------
#
#    ESP32 WiFi Camera (OV7670 FIFO Version)
#    ESP32WiFiCAM-OV7670
#
#    file:OV7670.py
#   

import utime
from machine import Pin, I2C
from micropython import const
from OV7670FIFO import OV7670FIFO

VGASIZE=(640, 480)
BAYERBPP=1

QQVGASIZE=(160, 120)
RGB565BPP=2

_OV7670ADDR = const(33)

_REG_GAIN = const(0x00)
_REG_BLUE = const(0x01)
_REG_RED = const(0x02)
_REG_COM1 = const(0x04)
_REG_VREF = const(0x03)
_REG_COM4 = const(0x0d)
_REG_COM5 = const(0x0e)
_REG_COM6 = const(0x0f)
_REG_AECH = const(0x10)
_REG_CLKRC = const(0x11)
_REG_COM7 = const(0x12)
_COM7_RGB = const(0x04)
_REG_COM8 = const(0x13)
_COM8_FASTAEC = const(0x80) 
_COM8_AECSTEP = const(0x40) 
_COM8_BFILT = const(0x20)  
_COM8_AGC = const(0x04)    
_COM8_AWB = const(0x02)   
_COM8_AEC = const(0x0)
_REG_COM9 = const(0x14)
_REG_COM10 = const(0x15)
_REG_COM14 = const(0x3E)
_REG_COM11 = const(0x3B)
_COM11_NIGHT = const(0x80)
_COM11_NMFR = const(0x60)
_COM11_HZAUTO = const(0x10)
_COM11_50HZ = const(0x08)
_COM11_EXP = const(0x0)
_REG_TSLB = const(0x3A)
_REG_RGB444 = const(0x8C)
_REG_COM15 = const(0x40)
_COM15_RGB565 = const(0x10)
_COM15_R00FF = const(0xc0)
_REG_HSTART = const(0x17)
_REG_HSTOP = const(0x18)
_REG_HREF = const(0x32)
_REG_VSTART = const(0x19)
_REG_VSTOP = const(0x1A)
_REG_COM3 = const(0x0C)
_REG_MVFP = const(0x1E)
_REG_COM13 = const(0x3d)
_COM13_UVSAT = const(0x40)
_REG_SCALING_XSC = const(0x70)
_REG_SCALING_YSC = const(0x71)
_REG_SCALING_DCWCTR = const(0x72)
_REG_SCALING_PCLK_DIV = const(0x73)
_REG_SCALING_PCLK_DELAY = const(0xa2)
_REG_BD50MAX = const(0xa5)
_REG_BD60MAX = const(0xab)
_REG_AEW = const(0x24)
_REG_AEB = const(0x25)
_REG_VPT = const(0x26)
_REG_HAECC1 = const(0x9f)
_REG_HAECC2 = const(0xa0)
_REG_HAECC3 = const(0xa6)
_REG_HAECC4 = const(0xa7)
_REG_HAECC5 = const(0xa8)
_REG_HAECC6 = const(0xa9)
_REG_HAECC7 = const(0xaa)
_REG_COM12 = const(0x3c)
_REG_GFIX = const(0x69)
_REG_COM16 = const(0x41)
_COM16_AWBGAIN = const(0x08)
_REG_EDGE = const(0x3f)
_REG_REG76 = const(0x76)
_ADCCTR0 = const(0x20)

_OV7670REGWAIT = 0.01
    
_BAYER_TRY_REGS = ((0x12, 0x80),
            (0x11, 0x01),
            (0x3a, 0x04),
            (0x12, 0x01),
            (0x17, 0x12),
            (0x18, 0x00),
            (0x32, 0xb6),
            (0x19, 0x02),
            (0x1a, 0x7a),
            (0x03, 0x00),
            (0x0c, 0x00),
            (0x3e, 0x00),
            (0x70, 0x3a),
            (0x71, 0x35),
            (0x72, 0x11),
            (0x73, 0xf0),
            (0xa2, 0x02),
            (0x13, 0xe0),
            (0x00, 0x00),
            (0x10, 0x00),
            (0x0d, 0x40),
            (0x14, 0x38),
            (0xa5, 0x07),
            (0xab, 0x08),
            (0x24, 0x95),
            (0x25, 0x33),
            (0x26, 0xe3),
            (0x9f, 0x78),
            (0xa0, 0x68),
            (0xa1, 0x0b),
            (0xa6, 0xd8),
            (0xa7, 0xd8),
            (0xa8, 0xf0),
            (0xa9, 0x90),
            (0xaa, 0x94),
            (0x13, 0xe5),
            (0x0e, 0x61),
            (0x0f, 0x4b),
            (0x16, 0x02),
            (0x21, 0x02),
            (0x22, 0x91),
            (0x29, 0x07),
            (0x33, 0x03),
            (0x35, 0x0b),
            (0x37, 0x1c),
            (0x38, 0x71),
            (0x3c, 0x78),
            (0x3d, 0x08),
            (0x41, 0x3a),
            (0x4d, 0x40),
            (0x4e, 0x20),
            (0x69, 0x55),
            (0x6b, 0x4a),
            (0x74, 0x19),
            (0x76, 0x61),
            (0x8d, 0x4f),
            (0x8e, 0x00),
            (0x8f, 0x00),
            (0x90, 0x00),
            (0x91, 0x00),
            (0x96, 0x00),
            (0x9a, 0x80),
            (0xb0, 0x8c),
            (0xb1, 0x0c),
            (0xb2, 0x0e),
            (0xb3, 0x82),
            (0xb8, 0x0a),
            (0x43, 0x14),
            (0x44, 0xf0),
            (0x45, 0x34),
            (0x46, 0x58),
            (0x47, 0x28),
            (0x48, 0x3a),
            (0x59, 0x88),
            (0x5a, 0x88),
            (0x5b, 0x44),
            (0x5c, 0x67),
            (0x5d, 0x49),
            (0x5e, 0x0e),
            (0x6c, 0x0a),
            (0x6d, 0x55),
            (0x6e, 0x11),
            (0x6f, 0x9f),
            (0x6a, 0x40),
            (0x01, 0x40),
            (0x02, 0x40),
            (0x13, 0xe7),
            (0x34, 0x11),
            (0x92, 0x66),
            (0x3b, 0x0a),
            (0xa4, 0x88),
            (0x96, 0x00),
            (0x97, 0x30),
            (0x98, 0x20),
            (0x99, 0x20),
            (0x9a, 0x84),
            (0x9b, 0x29),
            (0x9c, 0x03),
            (0x9d, 0x4c),
            (0x9e, 0x3f),
            (0x78, 0x04),
            (0x79, 0x01),
            (0xc8, 0xf0),
            (0x79, 0x0f),
            (0xc8, 0x20),
            (0x79, 0x10),
            (0xc8, 0x7e),
            (0x79, 0x0b),
            (0xc8, 0x01),
            (0x79, 0x0c),
            (0xc8, 0x07),
            (0x79, 0x0d),
            (0xc8, 0x20),
            (0x79, 0x09),
            (0xc8, 0x80),
            (0x79, 0x02),
            (0xc8, 0xc0),
            (0x79, 0x03),
            (0xc8, 0x40),
            (0x79, 0x05),
            (0xc8, 0x30),
            (0x79, 0x26))

#------------------------------------------------
#
#  OV7670 Image Sensor Control Class
#
#          
class OV7670():
    """OV7670 Image Sensor Conrol Class"""

    def __init__(self, scl, sda):

        self.FIFO = None               
        self.i2cAddr = None
        self.ov7670Stat = None

        self.i2c = I2C(scl=Pin(scl), sda=Pin(sda), freq=38400)
        utime.sleep(0.5)                # wait 500msec for i2c setup
        i2c_devices = self.i2c.scan() 
        # retuend value must be [33]
        if _OV7670ADDR in i2c_devices:
             print("found OV7670 Device")
             self.i2cAddr = _OV7670ADDR
             self.setup7670Regs()
             self.setQQVGARGB565Mode()
             self.ov7670Stat = True
        else:
             print("Error in I2C Setup")
             print("cannot find OV7670 Device")
             self.ov7670Stat = False

    def getStatus(self):
        """ Returns OV7670 setup status """
        return self.ov7670Stat

    def setupFIFO(self, spi, vsync, rdclk, we, rrst, wrst, pl):
        self.FIFO = OV7670FIFO(spi, vsync, rdclk, we, rrst, wrst, pl)

    def takePicture(self, verb=False):
        self.FIFO.takePicture(verb)

    def saveVGARawPicture(self, fileName=None):
        (width, height) = VGASIZE
        bpp = BAYERBPP
        if fileName is None:
            fileName = mylib.getPhotoFileNameWithPath('raw')
        state = self.FIFO.getImageAndSave(width * height * bpp, fileName)
        if state:
            return fileName
        else:
            return False

    def snapAndSaveVGARaw(self, fileName=None):
        (width, height) = VGASIZE
        bpp = BAYERBPP

        # switch to QQVGA -> VGA
        if True:
           self.setVGABayerMode()
        else:
           self.VGA_BAYER_TRY()
        self.takePicture()
        self.saveVGARawPicture(fileName)
        return fileName

    def FIFOReadReset(self):
        self.FIFO.readReset()

    def getPixelFromFIFO(self, buf, size, readReset=False):
        self.FIFO.getPixelFromFIFO(buf, size, readReset)

    def FIFOReadCLKOn(self):
        self.FIFO.rd_clk.on()

    def FIFOReadCLKOff(self):
        self.FIFO.rd_clk.off()

    def setQQVGARGB565Mode(self):
        self.QQVGARGB565()
  
    def setVGABayerMode(self):

        self.writereg(_REG_COM7, 0x01, True)  # bayer
        self.writereg(_REG_HSTART, 0x13, True)
        self.writereg(_REG_HSTOP, 0x01, True)
        self.writereg(_REG_HREF,0xb6, True)
        self.writereg(_REG_VSTART, 0x02, True)
        self.writereg(_REG_VSTOP, 0x7a, True)
        self.writereg(_REG_VREF,0x0a, True)
        self.writereg(_REG_COM3, 0x00, True)
        self.writereg(_REG_COM14, 0x00, True)
        self.writereg(_REG_COM15, 0xc0, True)  # b1100_0000
        self.writereg(_REG_SCALING_XSC, 0x3a, True)
        self.writereg(_REG_SCALING_YSC, 0x35, True)
        self.writereg(_REG_SCALING_DCWCTR, 0x11, True)
        self.writereg(_REG_SCALING_PCLK_DIV, 0xf0, True)
        self.writereg(_REG_SCALING_PCLK_DELAY, 0x02, True)

    def dumpReg(self):
        for reg in range(0, 0x100):
            if (reg % 16) == 0:
                print("\n[{:02x}]".format(reg), end="")
            val = self.readreg(reg)
            print(" {:02x}".format(val[0]), end="")
        print("")

    #----------------------------------------------------
    #
    #       Private Methods
    #
    def QQVGARGB565(self):
        self.writereg(_REG_COM7, 0b10000000, True)
        self.writereg(_REG_CLKRC, 0b10000000, True)
        self.writereg(_REG_COM11, 0b1000 | 0b10, True)
        self.writereg(_REG_COM7, 0b100, True)
        self.writereg(_REG_COM15, 0b11000000 | 0b010000, True)
        self.QQVGA()
        self.frameControl(196, 52, 8, 488)
        self.writereg(0xb0, 0x84, True)
        self.saturation(0)
        self.writereg(_REG_COM8, 0xe7, True)
        self.writereg(0x6f, 0x9f, True)
        self.writereg(_REG_VREF, 0x0a)
        self.writereg(_REG_HSTART, 0x16)
        self.writereg(_REG_HSTOP, 0x04)
        self.writereg(_REG_HREF, 0xa4)
     
    def QQVGA(self):
        self.writereg(_REG_COM3, 0x04, True)
        self.writereg(_REG_COM14, 0x1a, True)
        self.writereg(_REG_SCALING_XSC, 0x3a, True)
        self.writereg(_REG_SCALING_YSC, 0x35, True)
        self.writereg(_REG_SCALING_DCWCTR, 0x22, True)
        self.writereg(_REG_SCALING_PCLK_DIV, 0xf2, True)
        self.writereg(_REG_SCALING_PCLK_DELAY, 0x02, True)
    
    def frameControl(self, hStart, hStop, vStart, vStop):
        self.writereg(_REG_HSTART, hStart >> 3, True)
        self.writereg(_REG_HSTOP, hStop >> 3, True)
        self.writereg(_REG_HREF, ((hStop & 0b111) << 3) | (hStart & 0b111), True)
        self.writereg(_REG_VSTART, vStart >> 2, True)
        self.writereg(_REG_VSTOP, vStop >> 2, True)
        self.writereg(_REG_VREF, ((vStop & 0b11) << 2) | (vStart & 0b11), True)
    
    def saturation(self, s):
        self.writereg(0x4f, 0x80 + 0x20 * s, True)
        self.writereg(0x50, 0x80 + 0x20 * s, True)
        self.writereg(0x51, 0x00, True)
        self.writereg(0x52, 0x22 + int((0x11 * s) / 2), True)
        self.writereg(0x53, 0x5e + int((0x2f * s) / 2), True)
        self.writereg(0x54, 0x80 + 0x20 * s, True)
        self.writereg(0x58, 0x9e, True)
    
    def VGA_BAYER_TRY(self):
        for (reg, val) in BAYER_TRY_REGS:
            print("{:02x}, {:02x}".format(reg,val))
            self.writereg(reg, val)
            utime.sleep(0.1)
   
    def setup7670Regs(self):
        self.writereg(0x3a, 0x04)
        self.writereg(0x40, 0xd0)
        self.writereg(0x12, 0x14)
        self.writereg(0x32, 0x80)
        self.writereg(0x17, 0x16)
        self.writereg(0x18, 0x04)
        self.writereg(0x19, 0x02)
        self.writereg(0x1a, 0x7b)
        self.writereg(0x03, 0x06)
        self.writereg(0x0c, 0x00)
        self.writereg(0x3e, 0x00)
        self.writereg(0x70, 0x3a)
        self.writereg(0x71, 0x35)
        self.writereg(0x72, 0x11)
        self.writereg(0x73, 0x00)
        self.writereg(0xa2, 0x02)
        self.writereg(0x11, 0x81)
    	
        self.writereg(0x7a, 0x20)
        self.writereg(0x7b, 0x1c)
        self.writereg(0x7c, 0x28)
        self.writereg(0x7d, 0x3c)
        self.writereg(0x7e, 0x55)
        self.writereg(0x7f, 0x68)
        self.writereg(0x80, 0x76)
        self.writereg(0x81, 0x80)
        self.writereg(0x82, 0x88)
        self.writereg(0x83, 0x8f)
        self.writereg(0x84, 0x96)
        self.writereg(0x85, 0xa3)
        self.writereg(0x86, 0xaf)
        self.writereg(0x87, 0xc4)
        self.writereg(0x88, 0xd7)
        self.writereg(0x89, 0xe8)
    	
        self.writereg(0x13, 0xe0)
        self.writereg(0x00, 0x00)
    	
        self.writereg(0x10, 0x00)
        self.writereg(0x0d, 0x00)
        self.writereg(0x14, 0x28)
        self.writereg(0xa5, 0x05)
        self.writereg(0xab, 0x07)
        self.writereg(0x24, 0x75)
        self.writereg(0x25, 0x63)
        self.writereg(0x26, 0xA5)
        self.writereg(0x9f, 0x78)
        self.writereg(0xa0, 0x68)
        self.writereg(0xa1, 0x03)
        self.writereg(0xa6, 0xdf)
        self.writereg(0xa7, 0xdf)
        self.writereg(0xa8, 0xf0)
        self.writereg(0xa9, 0x90)
        self.writereg(0xaa, 0x94)
        self.writereg(0x13, 0xe5)
    
        self.writereg(0x0e, 0x61)
        self.writereg(0x0f, 0x4b)
        self.writereg(0x16, 0x02)
        self.writereg(0x1e, 0x37)
        self.writereg(0x21, 0x02)
        self.writereg(0x22, 0x91)
        self.writereg(0x29, 0x07)
        self.writereg(0x33, 0x0b)
        self.writereg(0x35, 0x0b)
        self.writereg(0x37, 0x1d)
        self.writereg(0x38, 0x71)
        self.writereg(0x39, 0x2a)
        self.writereg(0x3c, 0x78)
        self.writereg(0x4d, 0x40)
        self.writereg(0x4e, 0x20)
        self.writereg(0x69, 0x00)
        self.writereg(0x6b, 0x60)
        self.writereg(0x74, 0x19)
        self.writereg(0x8d, 0x4f)
        self.writereg(0x8e, 0x00)
        self.writereg(0x8f, 0x00)
        self.writereg(0x90, 0x00)
        self.writereg(0x91, 0x00)
        self.writereg(0x92, 0x00)
        self.writereg(0x96, 0x00)
        self.writereg(0x9a, 0x80)
        self.writereg(0xb0, 0x84)
        self.writereg(0xb1, 0x0c)
        self.writereg(0xb2, 0x0e)
        self.writereg(0xb3, 0x82)
        self.writereg(0xb8, 0x0a)
    
        self.writereg(0x43, 0x14)
        self.writereg(0x44, 0xf0)
        self.writereg(0x45, 0x34)
        self.writereg(0x46, 0x58)
        self.writereg(0x47, 0x28)
        self.writereg(0x48, 0x3a)
        self.writereg(0x59, 0x88)
        self.writereg(0x5a, 0x88)
        self.writereg(0x5b, 0x44)
        self.writereg(0x5c, 0x67)
        self.writereg(0x5d, 0x49)
        self.writereg(0x5e, 0x0e)
        self.writereg(0x64, 0x04)
        self.writereg(0x65, 0x20)
        self.writereg(0x66, 0x05)
        self.writereg(0x94, 0x04)
        self.writereg(0x95, 0x08)
        self.writereg(0x6c, 0x0a)
        self.writereg(0x6d, 0x55)
        self.writereg(0x6e, 0x11)
        self.writereg(0x6f, 0x9f)
        self.writereg(0x6a, 0x40)
        self.writereg(0x01, 0x40)
        self.writereg(0x02, 0x40)
        self.writereg(0x13, 0xe7)
        self.writereg(0x15, 0x00)  
    	
        self.writereg(0x4f, 0x80)
        self.writereg(0x50, 0x80)
        self.writereg(0x51, 0x00)
        self.writereg(0x52, 0x22)
        self.writereg(0x53, 0x5e)
        self.writereg(0x54, 0x80)
        self.writereg(0x58, 0x9e)
    	
        self.writereg(0x41, 0x08)
        self.writereg(0x3f, 0x00)
        self.writereg(0x75, 0x05)
        self.writereg(0x76, 0xe1)
        self.writereg(0x4c, 0x00)
        self.writereg(0x77, 0x01)
        self.writereg(0x3d, 0xc2)	
        self.writereg(0x4b, 0x09)
        self.writereg(0xc9, 0x60)
        self.writereg(0x41, 0x38)
        self.writereg(0x56, 0x40)
    	
        self.writereg(0x34, 0x11)
        self.writereg(0x3b, 0x02) 
    								
        self.writereg(0xa4, 0x89)
        self.writereg(0x96, 0x00)
        self.writereg(0x97, 0x30)
        self.writereg(0x98, 0x20)
        self.writereg(0x99, 0x30)
        self.writereg(0x9a, 0x84)
        self.writereg(0x9b, 0x29)
        self.writereg(0x9c, 0x03)
        self.writereg(0x9d, 0x4c)
        self.writereg(0x9e, 0x3f)
        self.writereg(0x78, 0x04)
    	
        self.writereg(0x79, 0x01)
        self.writereg(0xc8, 0xf0)
        self.writereg(0x79, 0x0f)
        self.writereg(0xc8, 0x00)
        self.writereg(0x79, 0x10)
        self.writereg(0xc8, 0x7e)
        self.writereg(0x79, 0x0a)
        self.writereg(0xc8, 0x80)
        self.writereg(0x79, 0x0b)
        self.writereg(0xc8, 0x01)
        self.writereg(0x79, 0x0c)
        self.writereg(0xc8, 0x0f)
        self.writereg(0x79, 0x0d)
        self.writereg(0xc8, 0x20)
        self.writereg(0x79, 0x09)
        self.writereg(0xc8, 0x80)
        self.writereg(0x79, 0x02)
        self.writereg(0xc8, 0xc0)
        self.writereg(0x79, 0x03)
        self.writereg(0xc8, 0x40)
        self.writereg(0x79, 0x05)
        self.writereg(0xc8, 0x30)
        self.writereg(0x79, 0x26) 
        self.writereg(0x09, 0x00)	
    
    def readreg(self, regAddr):
        self.i2c.writeto(self.i2cAddr, bytes([regAddr]))
        return self.i2c.readfrom(self.i2cAddr, 1)

    def writereg(self, reg, data, wait=False):
        self.i2c.writeto_mem(self.i2cAddr, reg, bytes([data]))
        if wait:
            utime.sleep(_OV7670REGWAIT)
        return None


#
# end of source
#

