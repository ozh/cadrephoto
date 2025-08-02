import smtplib
from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from utils.constants import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, OWNER_EMAIL
from utils.utils import debug_log


def tell_owner(sender_email):
    """
    Send a message to the owner (Mamie) with the sender's email.

    :param sender_email: Email of the sender.
    """
    debug_log(f"📧 Sending email to {OWNER_EMAIL} about new photo from {sender_email}", 'info')
    send_email_plaintext(sender_email, "Nouvelle photo reçue !", f"Hello Mamie,\n\nNouvelle photo reçue ! A découvrir sur le cadre photo !\n\nBisou (de la part de {sender_email})")


def tell_sender(to_email, image_path):
    """
    Send a message to the sender with the received photo.

    :param to_email: Email of the sender.
    :param image_path: Path to the image that was received.
    """
    debug_log(f"📧 Sending email to {to_email} with received photo", 'info')
    send_email_with_attachment(to_email, image_path)


def send_email_plaintext(from_email, subject, body):
    """
    Send a message to Mamie with the sender's email.

    :param from_email:
    :param subject:
    :param body:
    """
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = OWNER_EMAIL

    try:
        send_email_raw(msg)
        debug_log(f"📧 Mail sent to {OWNER_EMAIL} : new photo from {from_email}", 'info')
    except Exception as e:
        debug_log(f"Erreur lors de l'envoi du mail plaintext : {e}", 'critical')


def send_email_with_attachment(to_email, image_path):
    # Créer le message
    msg = MIMEMultipart('related')
    msg['Subject'] = "Photo reçue !"
    msg['From'] = SMTP_USER
    msg['To'] = to_email

    # Corps HTML avec image intégrée via CID
    html = """
    <html>
        <body>
            <p>Hello 👋,<br><br>
               Photo bien reçue ! Mamie est prévenue 😎<br>
               Ca ressemble (à peu près) à ça :</p>
            <p><img src="cid:image1"></p>
            <p>(message automatique, ne pas répondre)</p>
        </body>
    </html>
    """

    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)

    msg_text = MIMEText(html, 'html', 'utf-8')
    msg_alternative.attach(msg_text)

    # Lire l'image
    with open(image_path, 'rb') as img_file:
        img_data = img_file.read()

    mime_img = MIMEImage(img_data)
    mime_img.add_header('Content-ID', '<image1>')
    mime_img.add_header('Content-Disposition', 'inline', filename=Path(image_path).name)
    msg.attach(mime_img)

    # Envoi via SMTP (le serveur IMAP_SERVER est supposé être aussi SMTP)
    try:
        send_email_raw(msg)
        debug_log(f"✅ Email envoyé à {to_email}", 'info')
    except Exception as e:
        debug_log(f"❌ Erreur lors de l'envoi de l'email w/ attchmnt : {e}", 'critical')


def send_email_raw(msg):
    """
    Send a raw email message.

    :param msg: The email message to send.
    """
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)
