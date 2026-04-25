import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")


def send_line_notify(message: str):
    """Send a notification message via LINE Notify."""
    if not LINE_NOTIFY_TOKEN:
        print("[!] LINE_NOTIFY_TOKEN not found. Skipping LINE notification.")
        return False

    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"
    }
    data = {
        "message": message
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print("[*] LINE notification sent successfully.")
            return True
        else:
            print(f"[!] Failed to send LINE notification: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[!] Error sending LINE notification: {e}")
        return False


def send_email_notify(subject: str, message: str):
    """Send an email notification."""
    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
        print("[!] Email credentials not fully configured. Skipping Email notification.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain', 'utf-8'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print("[*] Email notification sent successfully.")
        return True
    except Exception as e:
        print(f"[!] Error sending Email notification: {e}")
        return False


def send_notifications(title: str, notion_url: str):
    """Wrapper to send both LINE and Email notifications."""
    message = f"\n報告已產生: {title}\n查看連結: {notion_url}"
    subject = f"Notion 報告已產生: {title}"
    
    send_line_notify(message)
    send_email_notify(subject, message)
