import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("POST_URL")
SMTP_PASSWORD = os.getenv("POST_KEY")

def send_notification_email(to_email: str, country: str, slot: tuple):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Подтверждение записи на визу"
        msg["From"] = SMTP_USER
        msg["To"] = to_email

        date, time = slot
        msg.set_content(
            f"Здравствуйте!\n\nВы успешно записаны на подачу документов на визу в {country}.\nДата: {date}\nВремя: {time}\n\nУдачи!")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(msg)
        print(f"Письмо успешно отправлено на {to_email}")
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")
        raise e

