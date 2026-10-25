import streamlit as st
import sqlite3
import datetime
import os
import zoneinfo
# ------------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING (FUN & COLORFUL VIBES)
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="College Farewell Memories 🎓",
    page_icon="🎓",
    layout="centered"
)

# Fun background & card styling
st.markdown("""
    <style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 50%, #A1C4FD 100%);
    }
    /* Friendly headings */
    h1, h2, h3 {
        color: #2D3748 !important;
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
    }
    /* Polaroid Card Effect for Messages */
    .memory-card {
        background-color: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 6px solid #FF6B6B;
    }
    </style>
""", unsafe_allow_html=True)

DB_PATH = "college_memories.db"
DRIVE_SYNC_DIR = "drive_backup_memories"

# ------------------------------------------------------------------------------
# DATABASE & FILE SETUP
# ------------------------------------------------------------------------------
def init_storage():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            friend_name TEXT NOT NULL,
            emoji TEXT NOT NULL,
            message TEXT NOT NULL,
            submitted_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    if not os.path.exists(DRIVE_SYNC_DIR):
        os.makedirs(DRIVE_SYNC_DIR)

init_storage()

def save_memory(name, emoji, message):
    # Set time zone to Indian Standard Time (IST)
    ist = zoneinfo.ZoneInfo("Asia/Kolkata")
    timestamp = datetime.datetime.now(ist).strftime("%d %B %Y, %I:%M %p")
    file_timestamp = datetime.datetime.now(ist).strftime("%Y%m%d_%H%M%S")

    # 1. Save into SQL Database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memories (friend_name, emoji, message, submitted_at)
        VALUES (?, ?, ?, ?)
    """, (name, emoji, message, timestamp))
    conn.commit()
    conn.close()

    # 2. Save text file locally
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
    filename = f"Memory_{safe_name}_{file_timestamp}.txt"
    filepath = os.path.join(LOCAL_BACKUP_DIR, filename)

    content = f"""========================================
COLLEGE FAREWELL MEMORY
========================================
From: {name}
Mood / Vibe: {emoji}
Date: {timestamp}
========================================

MESSAGE:
{message}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# ------------------------------------------------------------------------------
# WEBSITE HEADER
# ------------------------------------------------------------------------------
st.title("🎓Namma College Secret Diary✨")
st.markdown("### *College mudinjuchu da... adhunala manasula irukkuradha kottitu ponga* 💖")
st.write("canteen scene-u, mass bunk-u... future la open panni patha semma sirippa irukum ")

st.divider()

# ------------------------------------------------------------------------------
# FORM TO WRITE A MESSAGE
# ------------------------------------------------------------------------------
with st.form("memory_form", clear_on_submit=True):
    st.markdown("### 📝 Un Manasula Irukkuradha Kottu")
    
    friend_name = st.text_input("Yaaruda Nee? (Name Type Pannu) ✨", placeholder="Type your name here...")
    
    selected_emoji = st.selectbox(
        "Pick a Vibe / Emoji 😎",
        ["❤️ Love & Paasam","🎓 Clear Aayittom (Graduation)","🔥 Mass-u Boss-u","😂 Sirichu Sirichu Sethoda","🥳 Party Vibe Machan","🌟 Superstar DA","👑 Department Legend","🚀 Future-la Big Shot","✨ Semma Memories"]
    )
    
    message = st.text_area(
        "Your Memory / Message 💬",
        height=250,
        placeholder="Unakku enna thonudho adha eluthu❤️🥳✨"
    )
    
    # Live word counter (Unlimited display)
    words = len(message.split()) if message.strip() else 0
    st.caption(f"Current length: **{words:,} words** *(Unlimited)*")
    
    submit_button = st.form_submit_button(" Post My Memory 🚀", use_container_width=True)

# Submit action
if submit_button:
    if not friend_name.strip():
        st.error("Please enter your name first! 😊")
    elif not message.strip():
        st.error("Please write a small message before posting! 💬")
    else:
        chosen_emoji = selected_emoji.split()[0]  # Extracts just the emoji symbol
        save_memory(friend_name.strip(), chosen_emoji, message.strip())
        
        # Celebration Animation
        st.balloons()
        st.success("Thank you so much! Your memory has been posted below and saved forever! ❤️")
        st.rerun()

st.divider()

# ------------------------------------------------------------------------------
# LIVE MEMORY WALL (EVERYONE CAN READ)
# ------------------------------------------------------------------------------
st.markdown("## 💌 Namma Gang-oda Memories & Wishes")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT friend_name, emoji, message, submitted_at FROM memories ORDER BY id DESC")
rows = cursor.fetchall()
conn.close()

if rows:
    st.write(f"**Total Memories Posted:** `{len(rows)}`")
    for name, emoji, msg, time in rows:
        st.markdown(f"""
            <div class="memory-card">
                <h3 style="margin: 0; padding-bottom: 5px;">{emoji} <b>{name}</b></h3>
                <p style="font-size: 13px; color: #718096; margin-bottom: 15px;"><i>Posted on {time}</i></p>
                <p style="font-size: 16px; color: #2D3748; white-space: pre-wrap; line-height: 1.6;">{msg}</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("No memories posted yet! Be the first one to write above! ✨")
