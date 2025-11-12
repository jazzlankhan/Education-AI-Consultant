# ai_engine.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config import GEMINI_API_KEY
from database import get_db
from models import APILog
from sqlalchemy.orm import Session
import time
import json

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # Use stable version
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)

# === PROMPTS ===
SCORING_PROMPT = PromptTemplate.from_template("""
You are an education consultant AI. Score the lead (0-100) based on:
- Interest level
- Urgency
- Budget mention
- Specific course/program
- Readiness to enroll

Conversation:
{conversation}

Return JSON only:
{{"score": 85, "category": "MBA", "needs_human": true, "reason": "High urgency and budget mentioned"}}
""")

SUMMARY_PROMPT = PromptTemplate.from_template("""
Summarize this WhatsApp chat in 2-3 sentences. Extract:
- Name (if mentioned)
- Course interest
- Key concerns
- Next step

Conversation:
{conversation}

Return plain text summary.
""")

parser = JsonOutputParser()

def analyze_conversation(conversation: str, phone: str = None):
    """
    Analyzes conversation using Gemini and logs full API call details.
    Returns analysis result.
    """
    start_time = time.time()
    api_success = True
    api_error = None
    llm_prompt = conversation
    llm_response = None

    try:
        # === SCORING CHAIN ===
        scoring_chain = SCORING_PROMPT | llm | parser
        scoring_result = scoring_chain.invoke({"conversation": conversation})

        # === SUMMARY CHAIN ===
        summary_chain = SUMMARY_PROMPT | llm
        summary_response = summary_chain.invoke({"conversation": conversation})
        summary = summary_response.content.strip()

        # === BUILD RESPONSE ===
        llm_response = json.dumps({
            "score": scoring_result.get("score", 0),
            "category": scoring_result.get("category", "Unknown"),
            "needs_human": scoring_result.get("needs_human", False),
            "reason": scoring_result.get("reason", ""),
            "summary": summary
        }, ensure_ascii=False)

    except Exception as e:
        api_success = False
        api_error = str(e)
        print(f"Gemini Error for {phone}: {e}")
        llm_response = json.dumps({
            "score": 0,
            "category": "Error",
            "needs_human": False,
            "reason": "AI analysis failed",
            "summary": "Summary generation failed."
        })

    # === CALCULATE RESPONSE TIME ===
    response_time_ms = (time.time() - start_time) * 1000

    # === LOG TO DATABASE ===
    db: Session = next(get_db())
    log_entry = APILog(
        phone=phone or "unknown",
        message_type="llm_analysis",
        llm_prompt=llm_prompt,
        llm_response=llm_response,
        api_success=api_success,
        api_error=api_error,
        response_time_ms=response_time_ms
    )
    db.add(log_entry)
    db.commit()

    # === RETURN RESULT ===
    if api_success:
        result = json.loads(llm_response)
        return {
            "score": result.get("score", 0),
            "category": result.get("category", "Unknown"),
            "needs_human": result.get("needs_human", False),
            "reason": result.get("reason", ""),
            "summary": result.get("summary", "")
        }
    else:
        return {
            "score": 0,
            "category": "Error",
            "needs_human": False,
            "reason": api_error or "Unknown error",
            "summary": "Analysis failed due to API error."
        }