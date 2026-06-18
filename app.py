import streamlit as st
import engine
import urllib.parse

st.set_page_config(page_title="Chat Copilot Workspace", page_icon="💬", layout="wide")

st.title("💬 Chat Copilot Workspace")

# Pull available contacts from the database
try:
    conn = engine.sqlite3.connect("copilot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT contact_uid FROM chat_logs")
    contacts = [row[0] for row in cursor.fetchall()]
    conn.close()
except Exception:
    contacts = []

# Sidebar for choosing conversations
selected_contact = st.sidebar.selectbox("Select a conversation:", [""] + contacts)

if selected_contact:
    st.subheader(f"Managing Conversation: {selected_contact}")
    
    # 1. Main drafting section
    st.markdown("### 💡 Suggested Next Reply")
    
    # Simple simulator input to mock incoming texts
    incoming_text = st.text_input("Simulate incoming text from friend:")
    
    if incoming_text:
        # Generate the reply using your engine script
        draft_reply = engine.build_draft_reply(selected_contact, incoming_text)
        
        st.info(f"Draft: {draft_reply}")
        
        # --- THE WHATSAPP INTEGRATION ENGINE ---
        # Clean the phone number (remove spaces/pluses for the API link)
        clean_phone = selected_contact.replace("+", "").replace(" ", "").strip()
        # Safely encode the text spaces and characters for a web URL
        encoded_text = urllib.parse.quote(draft_reply)
        # Create the official WhatsApp deep-link scheme
        whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_text}"
        
        # Display the action button
        st.markdown(
            f'<a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">'
            f'<div style="background-color: #25D366; color: white; padding: 10px 20px; '
            f'text-align: center; border-radius: 8px; font-weight: bold; cursor: pointer;">'
            f'🚀 Open & Draft in WhatsApp'
            f'</div></a>', 
            unsafe_allow_index=True, unsafe_allow_html=True
        )
else:
    st.info("Please select or simulate a contact profile from the left sidebar to begin.")