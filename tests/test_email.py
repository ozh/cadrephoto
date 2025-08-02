import smtplib
import time
import imaplib

from utils.constants import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, IMAP_SERVER

print("Test IMAP connection...")
try:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(SMTP_USER, SMTP_PASSWORD)
    mail.select("INBOX")
    mail.close()
    mail.logout()
    print("IMAP connection successful.")
except Exception as e:
    print(f"IMAP connection failed: {e}")

time.sleep(1)

print("Test SMTP connection...")
try:
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.quit()
    print("SMTP connection successful.")
except Exception as e:
    print(f"SMTP connection failed: {e}")

print("End")
