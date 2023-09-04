import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from decouple import config

def send_email(filename, recipient_email):
    # Email configuration
    smtp_server = "smtp.gmail.com"  # Replace with your SMTP server
    smtp_port = 587  # Replace with the appropriate SMTP port
    smtp_username = "samira.test88@gmail.com"  # Replace with your email

    # Use decouple to securely retrieve the email password from the .env file
    smtp_password = config('EMAIL_PASSWORD')
    
    sender_email = "samira.test88@gmail.com"  # Replace with your email

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Excel Report"

    # Attach the Excel file
    attachment = open(filename, "rb")
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {filename}")
    msg.attach(part)

    # Connect to the SMTP server and send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()
