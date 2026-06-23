import streamlit as st
import engine
import urllib.parse
import sqlite3

st.set_page_config(page_title="Chat Copilot Workspace", page_icon="??", layout="wide")

st.title("?? Chat Copilot Workspace")

selected_contact = st.sidebar.text_input("Enter or paste phone number (e.g., +254711223344):")
conversation_goal = st.sidebar.text_area("Set a goal for this chat (Optional):", placeholder="e.g., Schedule a meetup")

st.sidebar.markdown("---")
sandbox_mode = st.sidebar.checkbox("?? Activate Personality Sandbox Mode", value=False)

if sandbox_mode:
    st.subheader("?? Personality Training Sandbox")
    st.markdown("""
    Use this space to talk to your AI like a friend. If it repeats itself, sounds too robotic, or uses phrases you wouldn't say, type a correction to update its style rules live!
    """)
    
    style_corrections = st.text_area(
        "?? Active Voice Corrections (What should the AI change?):",
        value=st.session_state.get("custom_voice_rules", ""),
        placeholder="e.g., Don't use 'bana' too much. When saying yes, use 'sawa' or 'fiti'. Keep sentences shorter."
    )
    st.session_state["custom_voice_rules"] = style_corrections

    st.markdown("---")
    
    sandbox_input = st.text_input("Type something you or a friend would normally say to test the response:")
    
    if sandbox_input:
        with st.spinner("Analyzing style rules..."):
            sandbox_draft = engine.build_draft_reply("SANDBOX_TEST", sandbox_input, conversation_goal, style_corrections)
        
        st.markdown("### ?? AI Sandbox Output:")
        st.info(f"**AI Draft:** {sandbox_draft}")
        st.caption("If this sounds accurate, perfect! If not, adjust the 'Active Voice Corrections' box above and hit Enter again.")

elif selected_contact:
    st.subheader(f"?? Active Thread: {selected_contact}")
    
    if conversation_goal:
        st.warning(f"?? **Current Conversation Goal:** {conversation_goal}")
    
    st.markdown("### ?? Recent Conversation History")
    try:
        conn = sqlite3.connect("copilot_memory.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sender, message_text FROM chat_logs 
            WHERE contact_uid = ? 
            ORDER BY timestamp DESC LIMIT 10
        """, (selected_contact,))
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            for sender, msg in reversed(rows):
                if sender == "Friend":
                    st.markdown(f"**?? Friend:** `{msg}`")
                else:
                    st.markdown(f"**? Mike:** *{msg}*")
        else:
            st.caption("No message history found for this number yet.")
    except Exception as e:
        st.caption(f"Timeline indexing setup... ({str(e)})")
        
    st.markdown("---")
    
    st.markdown("### ?? Input New Incoming Message")
    incoming_text = st.text_input("Paste the new text your friend just sent here:", key="new_message_input")
    
    if incoming_text:
        try:
            with st.spinner("Analyzing thread context..."):
                saved_rules = st.session_state.get("custom_voice_rules", "")
                draft_reply = engine.build_draft_reply(selected_contact, incoming_text, conversation_goal, saved_rules)
            
            st.markdown("### ?? AI Generated Response Draft")
            st.info(f"**Draft:** {draft_reply}")
            
            clean_phone = selected_contact.replace("+", "").replace(" ", "").strip()
            encoded_text = urllib.parse.quote(draft_reply)
            whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_text}"
            
            st.markdown(
                f'<a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">'
                f'<div style="background-color: #25D366; color: white; padding: 12px 20px; '
                f'text-align: center; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 10px;">'
                f'?? Open & Draft in WhatsApp'
                f'</div></a>', 
                unsafe_allow_html=True
            )
            
            if st.button("? Log My Sent Reply to Memory"):
                engine.log_message(selected_contact, "Mike", draft_reply)
                st.rerun()
                
        except Exception as e:
            st.error(f"Drafting Engine Error: {str(e)}")
else:
    st.info("Please enter a phone number or check 'Activate Personality Sandbox Mode' in the sidebar to begin.")
