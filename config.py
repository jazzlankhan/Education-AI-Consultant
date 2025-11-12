import os
from dotenv import load_dotenv

load_dotenv()

# === TWILIO ===
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC29bd738791ad82725fa5e69a06a0bef6")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "bd689423264b4f42b8106d9edaf5f530")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# === GEMINI ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyA2F8Po81tDGLkTU0Yr7heUrYTC68wu0Jg")

# === DATABASE (SQLite) ===
DATABASE_URL = "sqlite:///./leadbot.db"  # File-based DB
# === EMAIL ALERTS ===
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "your_email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_app_password")
ALERT_RECIPIENT = os.getenv("ALERT_RECIPIENT", "consultant@yourcompany.com")