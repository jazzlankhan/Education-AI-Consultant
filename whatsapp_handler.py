# whatsapp_handler.py
from fastapi import Request, APIRouter, Depends
from twilio.twiml.messaging_response import MessagingResponse
from database import get_db
from models import Lead, APILog
from ai_engine import analyze_conversation
from sqlalchemy.orm import Session
from config import TWILIO_WHATSAPP_NUMBER
from utils import send_hot_lead_email
import re
import time

router = APIRouter()

# In-memory conversation storage
conversations = {}

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    form = await request.form()
    incoming_msg = form.get("Body", "").strip()
    from_number = form.get("From", "").replace("whatsapp:", "")
    to_number = form.get("To", "")

    # Ignore if not for our bot
    if to_number != TWILIO_WHATSAPP_NUMBER:
        return ""

    # === LOG: Message Received ===
    received_log = APILog(
        phone=from_number,
        message_type="received",
        created_at=time.time()  # Will be overridden by DB default
    )
    db.add(received_log)

    # === Get or Create Lead ===
    lead = db.query(Lead).filter(Lead.phone == from_number).first()
    if not lead:
        lead = Lead(phone=from_number, status="new")
        db.add(lead)
        db.commit()
        db.refresh(lead)

    # === Store in Conversation Memory ===
    if from_number not in conversations:
        conversations[from_number] = ""
    conversations[from_number] += f"Lead: {incoming_msg}\n"

    # === Prepare Response ===
    resp = MessagingResponse()
    msg = resp.message()
    replied = False
    response_start_time = time.time()

    # === Extract Name (First Message) ===
    if not lead.name and any(kw in incoming_msg.lower() for kw in ["name", "i am", "my name"]):
        match = re.search(r"(?:name[:\s]*|i am|my name is)\s*([a-zA-Z\s]+)", incoming_msg, re.I)
        if match:
            lead.name = match.group(1).strip().title()
            db.commit()

    # === LLM Analysis After 3+ Messages ===
    msg_count = len([l for l in conversations[from_number].split("\n") if l.strip()])
    if msg_count >= 3:
        try:
            analysis = analyze_conversation(conversations[from_number], from_number)
            lead.score = analysis["score"]
            lead.category = analysis["category"]
            lead.chat_summary = analysis["summary"]
            lead.status = "hot" if analysis["needs_human"] else "warm"
            lead.last_message = incoming_msg
            db.commit()

            if analysis["needs_human"]:
                send_hot_lead_email({
                    "name": lead.name,
                    "phone": lead.phone,
                    "category": lead.category or "N/A",
                    "score": lead.score,
                    "reason": analysis["reason"],
                    "summary": analysis["summary"]
                })
                msg.body("Thank you! A human consultant will contact you shortly to discuss your goals.")
                replied = True
            else:
                # Auto-reply logic below
                pass
        except Exception as e:
            print(f"Analysis failed: {e}")
            # Still continue to reply

    # === Auto-Responses (Always Try to Reply) ===
    lower_msg = incoming_msg.lower()
    if any(g in lower_msg for g in ["hi", "hello", "hey", "good"]):
        msg.body("Hi! I'm your Education AI Assistant. What's your name and which course are you interested in?")
        replied = True
    elif any(c in lower_msg for c in ["mba", "ms", "bachelor", "ielts", "toefl", "gre"]):
        msg.body("Great choice! Are you a working professional or fresh graduate? Any target country or university?")
        replied = True
    elif any(b in lower_msg for b in ["budget", "fee", "cost", "price"]):
        msg.body("Thanks for sharing! Do you have a budget range in mind? (e.g., under $20k, $30k–50k)")
        replied = True
    elif any(t in lower_msg for t in ["thanks", "thank you", "okay", "got it"]):
        msg.body("You're welcome! Let me know when you're ready to proceed.")
        replied = True
    else:
        # Fallback
        msg.body("Tell me more — which country, timeline, or exam are you preparing for?")
        replied = True

    # === LOG: Replied or Unanswered ===
    response_time_ms = (time.time() - response_start_time) * 1000
    log_type = "replied" if replied else "unanswered"
    reply_log = APILog(
        phone=from_number,
        message_type=log_type,
        response_time_ms=response_time_ms
    )
    db.add(reply_log)
    db.commit()

    return str(resp)