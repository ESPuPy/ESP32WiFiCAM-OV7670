#-------------------------------------------
#
#    ESP32 WiFi Camera (OV7670 FIFO Version)
#    ESP32WiFiCAM-OV7670
#
#    file:OV7670FIFO.py
#   

from machine import Pin
import utime

class OV7670FIFO():
    """OV7670 FIFO Conrol class"""

    def __init__(self, spi, vsync, rdclk, we, rrst, wrst, pl):

        self.spi = spi
        self.vsync = Pin(vsync, Pin.IN)     # OV VSYNC          No39
        self.rd_clk = Pin(rdclk, Pin.OUT)   # FIFO ReadClock    No0
        self.we = Pin(we, Pin.OUT)          # FIFO Write Enable No26
        self.rrst = Pin(rrst, Pin.OUT)      # FIFO ReadReset    No21
        self.wrst = Pin(wrst, Pin.OUT)      # FIFO Write Reset  No22
        self.pl = Pin(pl, Pin.OUT)          # TTL PL            No25
        self.pl.on()
        self.rd_clk.on()                    # set RD CLK H

    #
    # from AL422 Data Sheets(Revision V1.1)
    #
    def readReset(self):
        """Reset FIFO Read Address"""
        self.rrst.on()           # set ReadReset:H
        self.rd_clk.on()
        self.rrst.off()          # set ReadReset:L
        self.rd_clk.off()
        self.rd_clk.on()
        self.rrst.on()           # set ReadReset:H

    def FIFOWriteReset(self):
        """Reset FIFO Write Address"""
        self.wrst.on()
        self.wrst.off()
        self.wrst.on()

    def FIFOWriteEnable(self):
        self.we.on()

    def FIFOWriteDisable(self):
        self.we.off()

    def readClockOneShot(self):   # RD_CLK:H->L->H
        self.rd_clk.on()
        self.rd_clk.off()
        self.rd_clk.on()

    def dumpFIFO(self, yy=16):
        for y in range(yy):
            for x in range(16):
                self.rd_clk.on()
                self.pl.off()
                self.pl.on()
                pixel = self.spi.read(1)
                print('{:02x} '.format(pixel[0]), end='')
                self.rd_clk.off()
            print('')


    def takePicture(self, verb=False):
        prevLevel=0
        weLevel=0
        takePicture=False

        self.FIFOWriteDisable()
        self.FIFOWriteReset()

        while not takePicture:
            nowLevel = self.vsync.value()
            if nowLevel == 1:     # Holizontal Sync
                if prevLevel == 0:   # Holizonal Sync L->H Edge
                    #print('\nL->H', end='')
                    if weLevel == 0:
                        self.FIFOWriteEnable()
                        weLevel=1
                        if verb:
                            print('Shutter On')
                    else:
                        self.FIFOWriteDisable()
                        weLevel=0      
                        takePicture=True
                        if verb:
                            print('Shutter Off')
            prevLevel=nowLevel

        if takePicture:
            print('OK! take picture')
        else:
            print('fail to take picture')
        self.FIFOWriteDisable()
        self.FIFOWriteReset()


    #
    #  buf.append() = self.spi.read(1)[0]   takes 4.57
    #
    def getPixelFromFIFO(self, buf, size, readReset=False):
        tmpBuf=bytearray(1)
        if readReset:
            self.readReset()
        for i in range(size):
            self.rd_clk.on()
            self.pl.off()
            self.pl.on()
            self.spi.readinto(tmpBuf)
            buf[i]=tmpBuf[0]
            self.rd_clk.off()

    def getImageAndSave(self, imageSize, fileName):
        BUFSIZE=512
        self.readReset()
        self.pl.on()
        print(fileName)
        s = utime.ticks_ms()
        f = open(fileName, mode='wb')
        scale=20   #  indicator max value is 20
        gaugeScale = int(imageSize/scale)

        buf=bytearray(BUFSIZE)
        for x in range(0, imageSize, BUFSIZE):
            self.getPixelFromFIFO(buf, BUFSIZE, False)
            f.write(buf)
            if (x % gaugeScale) == 0 :
                print('{:02d} '.format(scale - int(x/gaugeScale)), end='')
        f.close()
        print("\n")
        e = utime.ticks_ms()
        print("save time:{:d}(ms)".format(utime.ticks_diff(e, s)))

        return True    


