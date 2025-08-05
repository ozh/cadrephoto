from gpiozero import Button
from utils.display_next import get_next_photo, delete_current_photo
from utils.eink import send_to_eink
from utils.led import stop_blinking_led, start_blinking_led, led_on, led_off
from utils.utils import debug_log

# +--------+--------------------+------------------------------+
# | Button |       Press        |             Hold             |
# +--------+--------------------+------------------------------+
# | A      | Display next image | --                           |
# | B      | --                 | Delete current, display next |
# | C      | --                 | Display log                  |
# | D      | --                 | Shutdhown                    |
# +--------+--------------------+------------------------------+    # neat ! https://ozh.github.io/ascii-tables/ :)
#
# Disclaimer (and room for improvement): pressing a button during the sleep time will not interrupt the sleep in app.py
# This might lead to conflict, ie pressing a button to display next image while app is downloading a new image to display
# ¯\_(ツ)_/¯

def button_not_implemented(button, action):
    debug_log(f"Button {button} : {action} not implemented", 'info')

def button_shutdown_system():
    debug_log("Button D - shutdown", 'info')
    import utils.shutdown

def button_display_logs():
    import time
    from utils.logs import logs_to_image_first_screen, logs_to_image_second_screen
    led_on()
    debug_log("Button C - logs", 'info')
    debug_log('Displaying 1st screen', 'info')
    send_to_eink(logs_to_image_first_screen(), is_debug=True)
    debug_log('Sleeping for 20 seconds before displaying second screen', 'info')
    time.sleep(20)
    debug_log('Displaying 2nd screen', 'info')
    send_to_eink(logs_to_image_second_screen(), is_debug=True)
    led_off()
    debug_log('Done displaying debug screens. Press button again to refresh', 'info')

def button_display_next_image():
    debug_log("Button A - displaying next image", 'info')
    led_on()
    send_to_eink(get_next_photo())
    led_off()

def button_delete_current():
    debug_log("Button B - deleting current and display next", 'info')
    led_on()
    delete_current_photo()
    send_to_eink(get_next_photo())
    led_off()

# Define buttons with long press detection
button_a = Button(5, hold_time=2)
button_b = Button(6, hold_time=2)
button_c = Button(16, hold_time=2)
button_d = Button(24, hold_time=2)

button_a.when_pressed = button_display_next_image
button_a.when_held = lambda: button_not_implemented('A', 'long press')

button_b.when_pressed = lambda: button_not_implemented('B', 'press')
button_b.when_held = button_delete_current

button_c.when_pressed = lambda: button_not_implemented('C', 'press')
button_c.when_held = button_display_logs

button_d.when_pressed = lambda: button_not_implemented('D', 'press')
button_d.when_held = button_shutdown_system
