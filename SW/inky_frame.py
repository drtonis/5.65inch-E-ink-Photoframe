# from pimoroni import ShiftRegister, PWMLED
from machine import Pin, I2C, RTC
# from wakeup import get_shift_state, reset_shift_state
# from micropython import const
import pcf85063a
# import ntptime
import time

Led_Pins = [6, 7, 11, 12, 13, 14, 15] # all the LED pins, here we dont want to light any LED

HOLD_VSYS_EN = const(2)

RTC_ALARM = const(2)

i2c = I2C(0)
rtc = pcf85063a.PCF85063A(i2c)
# print(rtc.datetime())
i2c.writeto_mem(0x51, 0x00, b'\x00')  # ensure rtc is running (this should be default?)
rtc.enable_timer_interrupt(False)


# when using a new board write the local time to RTC
# get the local time of the PC
# time_local = time.localtime() 
# rtc.datetime((time_local[0], time_local[1], time_local[2], time_local[3], time_local[4], time_local[5], time_local[6]))

vsys = Pin(HOLD_VSYS_EN)
vsys.on()
# print("inky ON")

for i in range(len(Led_Pins)):
    Pin(Led_Pins[i]).off()
        
def LEDs_off():
    for i in range(len(Led_Pins)):
        Pin(Led_Pins[i]).off()
    
def inky_on():
    vsys.on()
#     print("inky ON 2")

def get_time():
    LEDs_off()
    return rtc.datetime() # year [0], month [1], day [2], hour [3], minute [4], second [5], day nr.

def sleep_for(minutes):
    year, month, day, hour, minute, second, dow = rtc.datetime()

    # if the time is very close to the end of the minute, advance to the next minute
    # this aims to fix the edge case where the board goes to sleep right as the RTC triggers, thus never waking up
    if second >= 55:
        minute += 1

    minute += minutes

    while minute >= 60:
        minute -= 60
        hour += 1

    if hour >= 24:
        hour -= 24

    rtc.clear_alarm_flag()
    rtc.set_alarm(0, minute, hour)
    rtc.enable_alarm_interrupt(True)

    turn_off()

    # Simulate sleep while on USB power
    while minutes > 0:
        time.sleep(60)
        minutes -= 1


def turn_off():
    LEDs_off() # just to be sure
    time.sleep(0.1)
    vsys.off()
