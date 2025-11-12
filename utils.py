# utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import pandas as pd
from io import BytesIO
from config import SMTP_SERVER, SMTP_PORT, EMAIL_USER, EMAIL_PASSWORD, ALERT_RECIPIENT

HOT_LEAD_TEMPLATE = """
<h2>New HOT Lead!</h2>
<p><strong>Name:</strong> {{ name or 'Not provided' }}</p>
<p><strong>Phone:</strong> {{ phone }}</p>
<p><strong>Course:</strong> {{ category }}</p>
<p><strong>Score:</strong> {{ score }}/100</p>
<p><strong>Reason:</strong> {{ reason }}</p>
<hr>
<h3>Chat Summary:</h3>
<p>{{ summary }}</p>
"""

def send_hot_lead_email(lead_data: dict):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = ALERT_RECIPIENT
        msg["Subject"] = f"Hot Lead - {lead_data['name'] or lead_data['phone']}"

        template = Template(HOT_LEAD_TEMPLATE)
        body = template.render(**lead_data)
        msg.attach(MIMEText(body, "html"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Email failed: {e}")

def export_leads_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode('utf-8')

def export_leads_to_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Leads")
    return output.getvalue()