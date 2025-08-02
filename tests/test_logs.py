import sys
import time

from utils.eink import send_to_eink
from utils.logs import logs_to_image_second_screen, logs_to_image_first_screen

send_to_eink(logs_to_image_first_screen(), is_debug=True)

if sys.platform != "win32":
    sleep_time = 15
    print(f"Sleeping for {sleep_time} seconds before displaying second screen of logs")
    time.sleep(sleep_time)

send_to_eink(logs_to_image_second_screen(), is_debug=True)

print("OK")
