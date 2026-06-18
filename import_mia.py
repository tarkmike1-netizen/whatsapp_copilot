import sqlite3
import re

# Set the operational mappings based on your file criteria
TARGET_FRIEND_NAME = "Mia"
TARGET_PHONE_NUMBER = "+254705656355"

def import_mia_history():
    print("Parsing text blocks inside WhatsApp Chat with Mia.txt...")
    
    conn = sqlite3.connect("copilot_memory.db")
    cursor = conn.cursor()
    
    # Enforce strict table schema safety guidelines
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_uid TEXT,
            sender TEXT,
            message_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    count = 0
    
    # Read the text file directly
    with open("WhatsApp Chat with Mia.txt", "r", encoding="utf-8") as file:
        for line in file:
            # Matches standard pattern: "DD/MM/YYYY, HH:MM - Sender: Message"
            match = re.search(r"\d{2}/\d{2}/\d{4},\s*\d{2}:\d{2}\s*-\s*([^:]*):\s*(.*)", line)
            
            if match:
                raw_sender = match.group(1).strip()
                message_text = match.group(2).strip()
                
                # Filter out standard WhatsApp system media omissions
                if "<Media omitted>" in message_text:
                    continue
                
                # Sort out who sent the text based on your explicit transcript names
                if raw_sender == TARGET_FRIEND_NAME:
                    sender_label = "Friend"
                elif raw_sender == "Mike" or raw_sender == "":
                    # Maps both your formal name entries and the blank early message tokens to you
                    sender_label = "Mike"
                else:
                    # Skip generic system events like encryption warnings
                    continue
                
                # Append into the relational rows
                cursor.execute(
                    "INSERT INTO chat_logs (contact_uid, sender, message_text) VALUES (?, ?, ?)",
                    (TARGET_PHONE_NUMBER, sender_label, message_text)
                )
                count += 1
                
    conn.commit()
    conn.close()
    print(f"\n✅ Success! Processed and injected {count} historical lines into your database.")

if __name__ == "__main__":
    import_mia_history()