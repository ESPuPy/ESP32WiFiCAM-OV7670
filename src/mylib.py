#-------------------------------------------
#
#    ESP32 WiFi Camera (OV7670 FIFO Version)
#    ESP32WiFiCAM-OV7670
#
#    file:mylib.py
#   

SYSDIR='/sd/sys'
TMPDIR='/sd/tmp'
PHOTODIR='/sd/DCIM'
DIFF_UTC_JST = 32400  #  JST = UTC + 9H (9 * 60 * 60)


import uos, ntptime, network
from micropython import mem_info
from gc import mem_free, collect, threshold
from utime import time, localtime
#from machine import RTC

#
# GC Functions
#
def reportMemory():
    return '{:d}'.format(mem_free())

def collectMemory(memoryMap=False):
    s = mem_free()
    collect()
    e = mem_free()
    reportText='{:d}->{:d}'.format(s, e)
    if memoryMap:
        mem_info(1)
    return reportText

def setGCThreshold(size):
    print('set setGCThreshold: {:d}'.format(size))
    threshold(size)


#
# connect WiFi 
#
def wlan_connect(essid, passwd):

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.disconnect()  # disconnect
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.connect(essid, passwd)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    return sta_if



#
# LocalTime(JST) Functions
#

def ntp_setup(): 
    status = None
    print('setup NTP:')
    ntp_hosts = ('ntp.nict.jp', 'time.google.com')
    for host in ntp_hosts:
        print('connect[{:s}]: '.format(host), end='')
        try:
            ntptime.host = host
            ntptime.settime()
        except Exception as e:
            print('Error! in ntptime.settime()')
            print(e)
        else:
            print('OK')
            status = True
            break
    if status == True:
        return True
    else:
        return False


def getLocalTimeJSTInSec():
    localJSTTime = time() + DIFF_UTC_JST
    return localJSTTime

def getLocalTimeJST():
    return localtime(getLocalTimeJSTInSec())

def getTodaysPhotoDIR():
    (year,month,date,hour,min,sec,weekday,yesterday) = getLocalTimeJST()
    return '{:s}/{:04d}{:02d}'.format(PHOTODIR,year,month)

def getPhotoName(format):
    (year,month,date,hour,min,sec,weekday,yesterday) = getLocalTimeJST()
    return '{:02d}{:02d}{:02d}_{:02d}{:02d}.{:s}'.format(year%100,month,date,hour,min,format)

def getPhotoFileNameWithPath(format='jpg'):
    filePath = getTodaysPhotoDIR()
    fileName = getPhotoName(format)
    return filePath + '/' + fileName

def getTimeStampJST(enableSecond=False):
    dt = getLocalTimeJST()
    if enableSecond:
        timeStamp = '{:d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}'.format(dt[0],dt[1],dt[2],dt[3],dt[4],dt[5])
    else:
        timeStamp = '{:d}/{:02d}/{:02d} {:02d}:{:02d}'.format(dt[0],dt[1],dt[2],dt[3],dt[4])
    return timeStamp

def setupSDFileSystem(sd):
    # check /sd/sys  in SD card
    if not isExists('/sd'):
        uos.mount(sd, '/sd')
    if not isExists(SYSDIR):
        uos.mkdir(SYSDIR)
    if not isExists(TMPDIR):
        uos.mkdir(TMPDIR)
    if not isExists(PHOTODIR):
        uos.mkdir(PHOTODIR)
    todaysPhotoDIR = getTodaysPhotoDIR()
    if not isExists(todaysPhotoDIR):
        uos.mkdir(todaysPhotoDIR)
    return True

def isExists(pathAndFile):
    pathList = pathAndFile.split('/')
    fileOrDir = pathList.pop()
    path = '/'.join(pathList)
    return fileOrDir in uos.listdir(path)

STAT_TYPE_FILE = 0x8000
STAT_TYPE_DIR = 0x4000

def getFileSize(fileName):
    try:
        stat = uos.stat(fileName)  
    except:
        print('Error in getFileSize')
        print('Exception at uos.stat()')
        return None
    else:
        if stat[0] == STAT_TYPE_FILE:
            return stat[6]  # filesize is at 7th in STAT (6 is because of 0 start)
        else:
            print('Error in getFileSize')
            print('not file')
            return None


