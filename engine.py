import os
import sqlite3
from google import genai
from google.genai import types

def build_draft_reply(contact_uid, incoming_text, conversation_goal=""):
    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
    # 🧠 LIVE DATABASE FETCH: Pull the actual chat history for this contact
    history_context = ""
    try:
        conn = sqlite3.connect("copilot_memory.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sender, message_text FROM chat_logs 
            WHERE contact_uid = ? 
            ORDER BY timestamp DESC LIMIT 6
        """, (contact_uid,))
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            # Format rows chronological for the AI to read
            history_lines = [f"{sender}: {msg}" for sender, msg in reversed(rows)]
            history_context = "\n".join(history_lines)
    except Exception:
        pass # Fallback smoothly if db is initializing

    # 🌟 THE FINAL VOICING & TEXT FLOW COMPASS
    system_instruction = f"""
    You are Mike's private AI chat copilot. Your job is to draft replies that sound EXACTLY like Mike chatting with friends on WhatsApp.
    
    CRITICAL STYLE BLUEPRINT:
    1. TONE & LANGUAGE: Casual, laid-back, blending Kenyan English and Sheng/Swahili naturally. No corporate capitalization or excessive punctuation.
    2. TEXTING FLOW (ANTI-REPETITION): Do not repeat yourself or stack multiple random questions together to look longer. Express a single, complete, natural thought or statement, followed by a maximum of ONE natural question or suggestion to keep the conversation going.
    3. RECENT THREAD MEMORY: Pay close attention to what was said previously so you don't repeat yourself or ignore what was just discussed.
    """
    
    if conversation_goal:
        system_instruction += f"\n4. STRATEGIC GOAL: Subtly work toward: '{conversation_goal}' without sounding mechanical or rushed."

    # Build a complete prompt stack that includes the live database history context
    full_prompt = "Here is the recent conversation history:\n"
    if history_context:
        full_prompt += f"{history_context}\n"
    else:
        full_prompt += "(No older history saved yet for this contact)\n"
        
    full_prompt += f"Friend just sent: '{incoming_text}'\n\nDraft Mike's next response:"
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=full_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.8
        )
    )
    
    return response.text.strip()

def log_message(contact_uid, sender, message_text):
    # Live cloud tracking database connector
    try:
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
        cursor.execute("""
            INSERT INTO chat_logs (contact_uid, sender, message_text) 
            VALUES (?, ?, ?)
        """, (contact_uid, sender, message_text))
        conn.commit()
        conn.close()
    except Exception:
        pass