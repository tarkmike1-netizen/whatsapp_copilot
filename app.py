import streamlit as st
import engine
import urllib.parse
import sqlite3

st.set_page_config(page_title="Chat Copilot Workspace", page_icon="💬", layout="wide")

st.title("💬 Chat Copilot Workspace")

# 1. Sidebar Inputs
selected_contact = st.sidebar.text_input("Enter or paste phone number (e.g., +254711223344):")

# New goal tracking box in the sidebar
conversation_goal = st.sidebar.text_area(
    "Set a goal for this chat (Optional):", 
    placeholder="e.g., Convince them to come through for Friday plan / Ask if they finished the assignment"
)

if selected_contact:
    st.subheader(f"📱 Active Thread: {selected_contact}")
    
    # Render the goal at the top if one is set
    if conversation_goal:
        st.warning(f"🎯 **Current Conversation Goal:** {conversation_goal}")
    
    # --- STEP 2: RENDERING THE LIVE CHAT TIMELINE ---
    st.markdown("### 🕒 Recent Conversation History")
    
    try:
        conn = sqlite3.connect("copilot_memory.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sender, message_text, timestamp FROM chat_logs 
            WHERE contact_uid = ? 
            ORDER BY timestamp DESC LIMIT 10
        """, (selected_contact,))
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            for sender, msg, time in reversed(rows):
                if sender == "Friend":
                    st.markdown(f"**👤 Friend:** `{msg}`")
                else:
                    st.markdown(f"**⚡ Mike:** *{msg}*")
        else:
            st.caption("No message history found for this number yet. Start typing below!")
    except Exception as e:
        st.caption(f"Timeline indexing setup... ({str(e)})")
        
    st.markdown("---")
    
    # --- STEP 3: INCOMING SIMULATOR ENGINE ---
    st.markdown("### 📥 Input New Incoming Message")
    incoming_text = st.text_input("Paste the new text your friend just sent here:", key="new_message_input")
    
    if incoming_text:
        try:
            with st.spinner("Analyzing thread context and drafting..."):
                # We now pass the conversation goal into our engine script
                draft_reply = engine.build_draft_reply(selected_contact, incoming_text, conversation_goal)
            
            st.markdown("### 💡 AI Generated Response Draft")
            st.info(f"**Draft:** {draft_reply}")
            
            # WhatsApp Deep-Linking Engine
            clean_phone = selected_contact.replace("+", "").replace(" ", "").strip()
            encoded_text = urllib.parse.quote(draft_reply)
            whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_text}"
            
            st.markdown(
                f'<a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">'
                f'<div style="background-color: #25D366; color: white; padding: 12px 20px; '
                f'text-align: center; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 10px;">'
                f'🚀 Open & Draft in WhatsApp'
                f'</div></a>', 
                unsafe_allow_html=True
            )
            
            if st.button("✅ Log My Sent Reply to Memory"):
                engine.log_message(selected_contact, "Mike", draft_reply)
                st.rerun()
                
        except Exception as e:
            st.error(f"Drafting Engine Error: {str(e)}")
else:
    st.info("Please enter a phone number in the left sidebar and press ENTER to initialize your workspace.")