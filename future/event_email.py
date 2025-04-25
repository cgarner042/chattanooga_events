#!/usr/bin/env python3
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import os
from pathlib import Path

# CONFIGURATION
SMTP_SERVER = "smtp.gmail.com"
PORT = 465  # For SSL
SENDER_EMAIL = "your.email@gmail.com"
APP_PASSWORD = "your-app-password"  # Gmail App Password
PRESET_RECIPIENTS = {
    "Work": "work@example.com",
    "Personal": "personal@gmail.com",
    "Team": "team@org.org"
}
CSV_PATH = Path.home() / "code" / "chattanooga_events" / "data" / "all_events.csv"
XLSX_PATH = CSV_PATH.with_suffix('.xlsx')

def send_email(recipients):
    """Send email with attachments"""
    msg = MIMEMultipart()
    msg['Subject'] = f"Chattanooga Events {formatdate(localtime=True)}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(recipients)
    
    # Email body
    body = """Attached:
    - Primary Data (XLSX)
    - Backup CSV copy"""
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach files
    for filepath in [XLSX_PATH, CSV_PATH]:
        with open(filepath, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{filepath.name}"'
        )
        msg.attach(part)
    
    # Send
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipients, msg.as_string())

def main():
    # Validate files
    if not CSV_PATH.exists():
        print(f"Error: Missing {CSV_PATH}")
        return
    
    if not XLSX_PATH.exists():
        print("XLSX not found. Converting...")
    
    # Recipient selection
    print("\nAvailable recipients:")
    for i, (name, email) in enumerate(PRESET_RECIPIENTS.items(), 1):
        print(f"  [{i}] {name:<10} {email}")
    
    choices = input(
        "Select recipients (numbers/comma-separated, c=custom, a=all): "
    ).strip().lower()
    
    if choices == 'a':
        recipients = list(PRESET_RECIPIENTS.values())
    elif choices == 'c':
        recipients = [input("Enter email address: ").strip()]
    else:
        recipients = []
        for choice in choices.split(','):
            try:
                idx = int(choice.strip()) - 1
                key = list(PRESET_RECIPIENTS.keys())[idx]
                recipients.append(PRESET_RECIPIENTS[key])
            except (ValueError, IndexError):
                print(f"Invalid selection: {choice}")
                return
    
    # Send email
    try:
        send_email(recipients)
        print(f"Email sent to: {', '.join(recipients)}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    main()