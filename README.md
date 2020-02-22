# ESP32WiFiCAM-OV7670(w/FIFO)
ESP32 WiFi Camera application has the following functions.

1. take pictures in VGA size and Bayer RAW format 
1. save pictures to the SD Memory card
1. upload pictures to the RAW Image Convert Service that is running on AWS
1. notify users using AWS SNS (Simple Notification Service)

Following parts are used

|parts type|parts name|
----|---- 
|MicroController|ESP32|
|Camera Unit|OV7670 Camera with FIFO|
|Monitor|1.8inch TFT LCD(ST7735)|
|Memory|SD Memory Card|

ESP32WiFiCAM is implemented in MicroPython

The following drivers are required to execute this application.

1. sdcard.py<br>https://github.com/micropython/micropython/tree/master/drivers/sdcard
1. ST7735.py<br>https://github.com/boochow/MicroPython-ST7735
1. terminalfont.py<br>https://github.com/GuyCarver/MicroPython/tree/master/lib

All files are subject to MIT license.
