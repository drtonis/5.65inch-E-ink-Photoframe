# An offline image gallery that switches between five jpg images
# Copy them into the root of your Pico's flash using Thonny.

from picographics import PicoGraphics, DISPLAY_INKY_FRAME as DISPLAY    # 5.7"
# from picographics import PicoGraphics, DISPLAY_INKY_FRAME_4 as DISPLAY  # 4.0"
# from picographics import PicoGraphics, DISPLAY_INKY_FRAME_7 as DISPLAY  # 7.3"
from machine import Pin, I2C, RTC, SPI, ADC
import pcf85063a
import time
import jpegdec
import sdcard
import uos
import os
import inky_frame

# # voltage_pin = Pin(26, mode=Pin.IN)
# analog_value = machine.ADC(0)
# reading = analog_value.read_u16() * 3.3 / 65535   
# print("ADC: ", reading , " V")
# 
# temp_sensor = machine.ADC(4)
# cpu_temp = 27 - (temp_sensor.read_u16() * 3.3 / 65535 - 0.706) / 0.001721 # Formula given in RP2040 Datasheet
# print("temperature: ", cpu_temp, " degC")

# set up the display
graphics = PicoGraphics(DISPLAY)
inky_frame.LEDs_off()  
def clear_screen():
    graphics.set_pen(1)
    graphics.clear()
    graphics.set_pen(0)
#     print("clear screen")

clear_screen()

sd = [] # just to check if we have sd card
# set up the SD card
sd_spi = SPI(0, sck=Pin(18, Pin.OUT), mosi=Pin(19, Pin.OUT), miso=Pin(16, Pin.OUT))
try:
    sd = sdcard.SDCard(sd_spi, Pin(22))
except:
    time.sleep(0.1)
    try:
        sd = sdcard.SDCard(sd_spi, Pin(22))
    except:
#         print("no SD card")
        graphics.set_pen(0)
        graphics.text("no SD card", 20, 20, scale=3)
        graphics.update()
        inky_frame.sleep_for(1440) # sleep time in minutes

try:
    uos.mount(sd, "/sd")
#     print("SD-card mounted")
except:
    time.sleep(0.1)
    uos.mount(sd, "/sd")
#     print("mount SD-card 2")
    
# find all the image files on the SD card
file_list_full = os.listdir("sd/") # list of all files on the SD-card
file_list = []
for element in file_list_full:
    if element.find('jpg') > 0:
        # we want only the .jpg files
        file_list.append(element)

# print(file_list)
inky_frame.LEDs_off()        
# Create a new JPEG decoder for our PicoGraphics
j = jpegdec.JPEG(graphics)

def display_image(filename):
    # clear display
    graphics.set_pen(1)
    graphics.clear()
    # Open the JPEG file
    j.open_file(filename)
#     print("file_name = " + str(filename))
    # Decode the JPEG
    j.decode(0, 0, jpegdec.JPEG_SCALE_FULL)
#     print("display image")
    # Display the result
    graphics.update()
        
if len(file_list) > 0:
    # help parameter to define which img should be shown
    file_nr = 0

    try:
        # read the file and print the contents to the console
        with open("/sd/inkytest.txt", "r") as f:
            file_nr = f.read()
#             print("file_nr = " + str(file_nr))
            f.close()
    except:
        pass
#         print("txt file doesn't exist")
    
    file_nr = int(file_nr)
    if file_nr >= len(file_list):
        file_nr = 0
#     print("file_nr = " + str(file_nr))
    
    file_write = file_nr
    file_write += 1
    if file_write >= len(file_list):
        file_write = 0
#     print("write txt file")
    # create a file and add some text, if this file already exists it will be overwritten
    with open("/sd/inkytest.txt", "w") as f:
        txt = str(file_write) + "\r\n"
        f.write(txt)
        f.close()
        
    show_now = "sd/" + str(file_list[file_nr])
    display_image(show_now)

else:
    graphics.set_pen(0)
    graphics.text("no img files", 10, 10, scale=3)
    graphics.update()
    # go to sleep for 24h
    inky_frame.sleep_for(1440) # sleep time in minutes

rtc_time = inky_frame.get_time()

# I would like to sleep till 00:00 - # rtc_time -> year [0], month [1], day [2], hour [3], minute [4], second [5], day nr.
sleep_time = 60 * (24 - rtc_time[3]) # hours to sleep - I'm assuming 24h time format
sleep_time -= rtc_time[4]

# for testing purpose change image after every 5 minutes
# sleep_time = 5 - rtc_time[4] % 5
# # print(sleep_time)

if sleep_time < 5:
    # just to be sure that we dont sleep less than 5 minutes
    sleep_time = 5

# print("sleeping...")
# go to sleep
inky_frame.sleep_for(sleep_time) # sleep time in minutes