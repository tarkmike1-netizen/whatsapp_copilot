import os
from google import genai
from google.genai import types

def build_draft_reply(contact_uid, incoming_text):
    # Retrieve the API key securely from Streamlit's environment settings
    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
    # 🌟 YOUR SYSTEM BLUEPRINT: This explicitly trains the AI on how you actually talk
    system_instruction = """
    You are Mike's private AI chat copilot. Your single job is to draft replies that sound EXACTLY like Mike.
    
    CRITICAL STYLE BLUEPRINT:
    1. TONE: Extremely casual, laid-back, concise, and effortless. Never sound like an AI assistant or enthusiastic customer care.
    2. LANGUAGE MIX: Use a natural mix of Kenyan English and casual Sheng/Swahili when appropriate, just like a normal chat with friends. 
    3. REPLIES TO PLANS: If someone suggests meeting up, hanging out, or plans for Friday, do NOT use generic Western slang like "Say less". Instead, say things like "Rada?", "Form ni gani?", "Sawa, tucheki", or keep it simple and chilled.
    4. LENGTH: Keep sentences incredibly brief. Usually 2 to 6 words max. No corporate capitalization or excessive punctuation.
    """
    
    # Simple prompt passing the context to the model
    prompt = f"Friend says: '{incoming_text}'. Draft a natural response in Mike's voice."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7 # Keeps the wording creative but grounded
        )
    )
    
    return response.text.strip()

def log_message(contact_uid, sender, message_text):
    # Dummy placeholder function to keep app.py happy in the cloud environment
    pass