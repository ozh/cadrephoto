import sys
from datetime import timedelta, datetime
from utils.check_new import check_mail_and_download_attachments
from utils.constants import DITHERED_IMAGE_PATH, CHECK_INTERVAL, DISPLAY_PHOTO_INTERVAL
from utils.display_next import display_next_image
from utils.eink import send_to_eink
from utils.email import tell_sender, tell_owner
from utils.image_manipulation import process_new_image
from utils.led import stop_blinking_led, start_blinking_led
from utils.utils import *

if sys.platform != "win32":
    from utils.buttons import *


def run_app():
    last_display_time = datetime.min
    min_display_duration = timedelta(seconds=DISPLAY_PHOTO_INTERVAL)
    debug_log(f"Starting application - {last_display_time} ; display {min_display_duration}", 'info')

    while True :
        start_blinking_led()

        now = datetime.now()
        debug_log(f"(re)starting loop -- {now}", 'info')

        # Case 1 : we have a new mail with an image attachment
        if mail_image := check_mail_and_download_attachments():
            # mail_image is a tuple (sender_email, attachment_path)
            sender_email, attachment_path = mail_image
            debug_log(f"Sender : {sender_email}", 'info')
            debug_log(f"Attachment : {attachment_path}", 'info')

            image_name, dithered_image_path = process_new_image(attachment_path, DITHERED_IMAGE_PATH)

            # Display new image on Pimoroni, tell sender and tell recipient
            send_to_eink(image_name)
            tell_sender(sender_email, dithered_image_path)
            tell_owner(sender_email)

            last_display_time = now

        # Case 2 : no new image, but it's been more than 1 hour since the last display
        elif now - last_display_time >= min_display_duration:
            debug_log("Displaying next image", 'info')
            display_next_image()
            last_display_time = now

        # Case 3 : no new mail, and it's been less than 1 hour since the last display
        else:
            # nothing to do
            debug_log("No new mail, and it's been less than 1 hour since the last display", 'info')
            pass

        # Wait for CHECK_INTERVAL minutes before checking again
        debug_log(f"Sleeping for {CHECK_INTERVAL} seconds", 'info')
        stop_blinking_led()
        time.sleep(CHECK_INTERVAL)

        # Disclaimer (and room for improvement): pressing a button during the sleep time will not interrupt the sleep.
        # This might lead to conflict, ie pressing a button to display next image while app is downloading a new image to display
        # ¯\_(ツ)_/¯


if __name__ == "__main__":
    try:
        run_app()
    except KeyboardInterrupt:
        debug_log("Ctrl^C -> Exiting application.", "critical")
        stop_blinking_led()
        exit_program(0)
    except Exception as e:
        debug_log(f"An error occurred trying to run_app(): {e}", "critical")
        stop_blinking_led()
        exit_program(1)
