import smtplib
import time
import imaplib

from utils.constants import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, IMAP_SERVER, OWNER_EMAIL
from utils.email import tell_owner, tell_sender
from utils.logs import connection_test_imap, connection_test_smtp

print("Test IMAP connection...")
print(connection_test_imap())
time.sleep(0.5)

print("Test SMTP connection...")
print(connection_test_smtp())
time.sleep(0.5)

print("Sending test email to owner...")
tell_owner('noreply@test-email.null')

print("End")
