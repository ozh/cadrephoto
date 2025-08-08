import sys
import threading
import time

from utils.constants import MAX_BLINKS

if sys.platform != "win32":
    import gpiod
    import gpiodevice
    from gpiod.line import Bias, Direction, Value
    LED_PIN = 13
    # Find the gpiochip device we need
    chip = gpiodevice.find_chip_by_platform()
    # Setup for the LED pin
    led = chip.line_offset_from_id(LED_PIN)
    gpio = chip.request_lines(consumer="inky",
                              config={led: gpiod.LineSettings(direction=Direction.OUTPUT, bias=Bias.DISABLED)})


stop_event = threading.Event() # Global event to control the blinking thread
blink_thread = None            # thread ref
blinks_iteration = 0           # count number of blinks in the current thread

def led_on():
    if sys.platform != "win32":
        gpio.set_value(led, Value.ACTIVE)
    else:
        print("O", end=' ')

def led_off():
    if sys.platform != "win32":
        gpio.set_value(led, Value.INACTIVE)
    else:
        print(".", end=' ')

def blink_led():
    global blinks_iteration
    while not stop_event.is_set() and blinks_iteration <= MAX_BLINKS :
        blinks_iteration+= 1
        led_on()
        time.sleep(0.3)
        led_off()
        time.sleep(1)

def start_blinking_led():
    global blink_thread
    stop_event.clear()
    blink_thread = threading.Thread(target=blink_led)
    blink_thread.start()

def stop_blinking_led():
    global blinks_iteration
    blinks_iteration = 0
    stop_event.set()
    if blink_thread is not None:
        blink_thread.join()

