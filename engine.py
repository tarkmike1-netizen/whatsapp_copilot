import os
from google import genai
from google.genai import types

def build_draft_reply(contact_uid, incoming_text, conversation_goal=""):
    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
    # Base personality blueprint
    system_instruction = """
    You are Mike's private AI chat copilot. Your job is to draft replies that sound EXACTLY like Mike, matching the flow of a real friend-to-friend text chat.
    
    CRITICAL STYLE BLUEPRINT:
    1. TONE: Extremely casual, laid-back, and natural. Never sound formal, stiff, or like an AI assistant. No corporate capitalization or excessive punctuation.
    2. LANGUAGE MIX: Freely use a smooth blend of casual Kenyan English and Sheng/Swahili (like 'rada', 'form', 'kuishia', 'mambo', etc.) depending on what the friend said.
    3. EXTRAS & EXPRESSION: Give a complete, conversational thought, ask a follow-up question, or suggest an idea in Mike's voice so the conversation keeps flowing naturally.
    """
    
    # Dynamically inject the goal instruction if you set one
    if conversation_goal:
        system_instruction += f"\n4. STRATEGIC GOAL: The current overarching goal for this specific conversation is: '{conversation_goal}'. Without sounding obvious or forced, subtly steer your response or follow-up thoughts to work toward achieving this goal."
    
    prompt = f"Friend says: '{incoming_text}'. Draft a natural, conversational response in Mike's voice that moves toward the goal if possible."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.85
        )
    )
    
    return response.text.strip()

def log_message(contact_uid, sender, message_text):
    pass