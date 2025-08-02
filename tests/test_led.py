import time
from utils.led import led_on, led_off, start_blinking_led, stop_blinking_led

print("LED on")
try:
    led_on()
except Exception as e:
    print(f"Could not turn LED on: {e}")
time.sleep(3)

print("LED off")
try:
    led_off()
except Exception as e:
    print(f"Could not turn LED off: {e}")
time.sleep(1)

print("LED blinking")
try:
    start_blinking_led()
except Exception as e:
    print(f"Could not start blinking LED: {e}")
print("Sleep 10")
time.sleep(10)  # Let it blink for 10 seconds
try:
    stop_blinking_led()
except Exception as e:
    print(f"Could not stop blinking LED: {e}")
print("End")
