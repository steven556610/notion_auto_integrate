import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_ASSESS_TOKEN")
USER_ID = os.getenv("USER_ID")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")


def send_line_notify(message: str):
    """Send a notification message via LINE Messaging API."""
    if not LINE_ACCESS_TOKEN or not USER_ID:
        print("[!] LINE_ASSESS_TOKEN or USER_ID not found in .env. Skipping LINE notification.")
        return False

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
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
    """Wrapper to send notifications. Currently uses LINE only."""
    message = f"\n報告已產生: {title}\n查看連結: {notion_url}"
    
    send_line_notify(message)
    # Email 通知
    subject = f"Notion 報告已產生: {title}"
    send_email_notify(subject, message)
