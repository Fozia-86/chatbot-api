import os
import re
from fastapi import FastAPI
from pydantic import BaseModel
from rapidfuzz import process, fuzz
from google import genai
from database import conn, cursor
from dotenv import load_dotenv

# --------------------
# 1. Setup & Initialization
# --------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)
app = FastAPI(title="Hybrid FAQ Chatbot")


def track_order(user_query):
    # Pattern 1: #12345 format
    # Pattern 2: "order" keyword + number
    # Pattern 3: koi bhi number
    patterns = [
        (r"#(\d+)", "# se"),
        (r"order.*?(\d+)", "order + number"),
        (r"\d+", "koi bhi number")
    ]

    for pattern, source in patterns:
        match = re.search(pattern, user_query, re.IGNORECASE)
        if match:
            # agar pattern mein brackets hon (group 1), to group(1) use karo
            # warna group(0) use karo (pura match)
            order_id = match.group(1) if match.lastindex else match.group(0)
            return f"Order #{order_id} dispatched hai aur 2-3 din me deliver ho jayega."

    # agar koi bhi number na mile
    return "Order track karne ke liye apna order number bhejein, e.g. 'Order #12345'."


# --------------------
# 2. Data & Models
# --------------------
faqs = [
    {"q": "Aapka office kahan hai?", "a": "Humara office Karachi, Pakistan mein hai."},
    {"q": "Delivery kitne din mein hoti hai?", "a": "3 se 5 working days."},
    {"q": "Refund policy kya hai?", "a": "7 din ke andar refund available hai."},
    {"q": "Cash on Delivery available hai?", "a": "Ji haan COD available hai."},
    {"q": "Delivery charges kitne hain?", "a": "Rs. 150, 2000+ par free."},
]

faq_questions = [faq["q"] for faq in faqs]

class UserQuery(BaseModel):
    question: str

# --------------------
# 3. Helper Functions
# --------------------
def get_gemini_response(question: str):
    try:
        prompt = f"""Tum aik polite aur friendly customer-support assistant ho.
Hamesha asaan Roman Urdu mein, narm lehje mein, aur mukhtasar jawab do (2-3 lines).

User ka sawal: {question}"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"GEMINI ERROR: {e}")
        return "Maazrat, filhal main sawal ka jawab nahi de paa raha."

def route_query(user_query, score, threshold):
    if score >= threshold:
        return "faq"
    elif "order" in user_query.lower():
        return "order"
    else:
        return "ai"


# 4. Endpoints
# --------------------

@app.post("/ask")
async def ask_bot(query: UserQuery):
    user_q = query.question
    
    # Fuzzy Matching
    match = process.extractOne(user_q, faq_questions, scorer=fuzz.WRatio)
    score = match[1] if match else 0
    
    decision = route_query(user_q, score, threshold=88)

    if decision == "faq":
        matched_question = match[0]
        for item in faqs:
            if item["q"] == matched_question:
                answer = item["a"]
                route = "FAQ"
                break
    elif decision == "order":
        answer = track_order(user_q)
        route = "Order"
    else:
        answer = get_gemini_response(user_q)
        route = "Gemini AI"

    # --- History Update (DB) ---
    cursor.execute(
        "INSERT INTO chat_history (question, answer) VALUES (%s, %s)",
        (user_q, answer)
    )
    conn.commit()

    cursor.execute("""
        SELECT question, answer
        FROM chat_history
        ORDER BY id DESC
        LIMIT 5
    """)
    history = cursor.fetchall()

    return {
        "answer": answer,
        "route": route,
        "history": history
    }

@app.get("/")
def home():
    return {"message": "Hybrid Chatbot is online! 🚀"}

@app.get("/history")
def get_history():
    cursor.execute("SELECT question, answer FROM chat_history")
    return {"chat_history": cursor.fetchall()}

if __name__ == "__main__":
    import uvicorn
    # Platform apna PORT deta hai, warna default 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)