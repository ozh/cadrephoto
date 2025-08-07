import os
from dotenv import load_dotenv

load_dotenv(override=True) # Value of that variable in the .env file, then in the environment

IMAP_SERVER = os.getenv("IMAP_SERVER")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

OWNER_EMAIL = os.getenv("OWNER_EMAIL")
EMAIL_CONFIRMATION_SUBJECT= os.getenv("EMAIL_CONFIRMATION_SUBJECT")
EMAIL_CONFIRMATION_BODY = os.getenv("EMAIL_CONFIRMATION_BODY")
EMAIL_OWNER_SUBJECT= os.getenv("EMAIL_OWNER_SUBJECT")
EMAIL_OWNER_BODY = os.getenv("EMAIL_OWNER_BODY")

DEBUG = (os.getenv("DEBUG").lower() == 'true')
MAX_BLINKS = int(os.getenv("MAX_BLINKS", 200))
NUMBER_OF_PHOTOS_TO_KEEP = int(os.getenv("NUMBER_OF_PHOTOS_TO_KEEP", 5))
DISPLAY_PHOTO_INTERVAL = int(os.getenv("DISPLAY_PHOTO_INTERVAL", 3600))  # in seconds
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 10))  # in seconds

SHUTDOWN_MESSAGE_LINE1= os.getenv("SHUTDOWN_MESSAGE_LINE1")
SHUTDOWN_MESSAGE_LINE2= os.getenv("SHUTDOWN_MESSAGE_LINE2")

# File parameters
TMP_DOWNLOAD_FOLDER = "./temp_download"
OUTPUT_FOLDER = "./photos"
CURRENT_PHOTO = "./current_photo.txt"
DITHERED_IMAGE_PATH = "./output_dithered.jpg"

# Simulated palette Spectra6 for the email confirmation
PALETTE = [
    (230, 45, 45),  # Soft red (less saturated, vermillion)
    (60, 180, 100),  # Pastel green
    (50, 100, 190),  # Soft blue (light purple)
    (255, 220, 60),  # Pale yellow
    (20, 20, 20),  # Black (not pure, highlights)
    (245, 245, 245)  # Off-white
]
