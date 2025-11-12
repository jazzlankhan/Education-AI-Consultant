# main.py
from fastapi import FastAPI
from whatsapp_handler import router as whatsapp_router
from database import engine
from models import Base

app = FastAPI(title="Education Consultant AI")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include WhatsApp webhook
app.include_router(whatsapp_router)

@app.get("/")
def home():
    return {"message": "Education AI Bot is LIVE!"}

# Optional: Health check
@app.get("/health")
def health():
    return {"status": "healthy"}