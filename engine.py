import sqlite3
import os
from google import genai
from google.genai import types

# 1. Inject your verified API key into the script configuration
YOUR_SECRET_KEY = os.environ.get("GEMINI_API_KEY", "")
os.environ["GOOGLE_API_KEY"] = YOUR_SECRET_KEY

# 2. Define the personality guidelines for your copy-paste drafting assistant
SYSTEM_GHOSTWRITER_INSTRUCTION = """
You are Mike's personal messaging ghostwriter. Your sole job is to draft his next response.
To match his voice perfectly, study these golden rules of his typing style:
- Keep it extremely brief. Usually 3 to 6 words. Single-sentence answers only.
- Never use formal corporate words, punctuation overload, or emojis unless he uses them in the samples.
- Match his vocabulary (e.g., uses phrases like "You know it", "Say less", "Safe", "Link up").

Here are perfect examples of how Mike responds to friends. Mimic this exact tone:

Example 1:
Friend: Yo, are we still tracking for leg day at the gym later?
Mike: You know it

Example 2:
Friend: Awesome. What time should I head over?
Mike: Link up at 5

Example 3:
Friend: I'm on my way now.
Mike: Safe, let me know when you're outside

Example 4:
Friend: Can you check that file later?
Mike: Yeah, I got you

Strict Rule: Output ONLY the raw text draft for Mike. Do not add quotes, do not say "Here is your draft", and do not add any extra text.
"""

def init_database():
    """Creates a local database file to log message history for context memory."""
    conn = sqlite3.connect("copilot_memory.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_uid TEXT,
            sender TEXT,
            message_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_message(contact_uid: str, sender: str, text: str):
    """Saves a message to the database timeline."""
    conn = sqlite3.connect("copilot_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_logs (contact_uid, sender, message_text) VALUES (?, ?, ?)",
        (contact_uid, sender, text)
    )
    conn.commit()
    conn.close()

def build_draft_reply(contact_uid: str, new_incoming_text: str) -> str:
    """Logs incoming texts, reads history context, and gets a perfect draft from Gemini."""
    init_database()
    
    # Log the friend's incoming text
    log_message(contact_uid, "Friend", new_incoming_text)
    
    # Pull the last 5 exchanges to feed to Gemini's short-term memory
    conn = sqlite3.connect("copilot_memory.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, message_text FROM chat_logs 
        WHERE contact_uid = ? 
        ORDER BY timestamp DESC LIMIT 5
    """, (contact_uid,))
    rows = cursor.fetchall()
    conn.close()
    
    # Re-order oldest to newest so the conversation timeline reads naturally
    ordered_history = list(reversed(rows))
    
    # Build a clean conversation transcript string
    history_compiled = ""
    for sender, msg in ordered_history:
        # Strip out any residual system symbols if they appear
        clean_msg = str(msg).replace("<This message was edited>", "").strip()
        history_compiled += f"{sender}: {clean_msg}\n"
        
    # Generate the draft using the official Client
    client = genai.Client()
    
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_GHOSTWRITER_INSTRUCTION,
        temperature=0.7,
        max_output_tokens=150  # Prevent abrupt truncations
    )
    
    # Explicit timeline positioning for structural prompt formatting
    prompt_payload = f"""
Analyze the recent message flow between Mike and his friend. Write the next natural response for Mike based on his personality profile.

[CONVERSATION TIMELINE]
{history_compiled}

Output the response draft directly below. Do not wrap it in quotes or add metadata text.
Mike:"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_payload,
        config=config
    )
    
    final_output = response.text.strip()
    if len(final_output) <= 1:
        return "Rada"
        
    return final_output