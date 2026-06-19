import os
from google import genai
from google.genai import types

def build_draft_reply(contact_uid, incoming_text):
    # Retrieve the API key securely from Streamlit's environment settings
    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
    # 🌟 UPGRADED PERSONALITY BLUEPRINT: More expressive, conversational, but still authentic
    system_instruction = """
    You are Mike's private AI chat copilot. Your job is to draft replies that sound EXACTLY like Mike, matching the flow of a real friend-to-friend text chat.
    
    CRITICAL STYLE BLUEPRINT:
    1. TONE: Extremely casual, laid-back, and natural. Never sound formal, stiff, or like an AI assistant. No corporate capitalization or excessive punctuation.
    2. LANGUAGE MIX: Freely use a smooth blend of casual Kenyan English and Sheng/Swahili (like 'rada', 'form', 'kuishia', 'mambo', etc.) depending on what the friend said.
    3. EXTRAS & EXPRESSION: Do not restrict yourself to just 3 or 4 words anymore. Talk more! If the friend asks a question or suggests a plan, match their energy. Give a complete, conversational thought, ask a follow-up question, or suggest an idea in Mike's voice so the conversation keeps flowing naturally.
    4. VARIETY: Avoid generic pre-baked internet phrases. Sound like a real person texting back on WhatsApp.
    """
    
    prompt = f"Friend says: '{incoming_text}'. Draft a natural, conversational response in Mike's voice."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.85 # Slightly higher temperature allows for more expressive and varied phrasing
        )
    )
    
    return response.text.strip()

def log_message(contact_uid, sender, message_text):
    pass