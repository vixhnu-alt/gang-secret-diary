import streamlit as st
import sqlite3
import datetime
import zoneinfo
import os

# ------------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="College Farewell Memories 🎓",
    page_icon="🎓",
    layout="centered"
)

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 50%, #A1C4FD 100%);
    }
    h1, h2, h3 {
        color: #2D3748 !important;
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
    }
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
LOCAL_BACKUP_DIR = "drive_backup_memories"

# 🔑 SET YOUR SECRET ADMIN PASSWORD HERE
ADMIN_PASSWORD = "Arovis@191025"

# ------------------------------------------------------------------------------
# DATABASE SETUP
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

    if not os.path.exists(LOCAL_BACKUP_DIR):
        os.makedirs(LOCAL_BACKUP_DIR)

init_storage()

def save_memory(name, emoji, message):
    ist = zoneinfo.ZoneInfo("Asia/Kolkata")
    timestamp = datetime.datetime.now(ist).strftime("%d %B %Y, %I:%M %p")
    file_timestamp = datetime.datetime.now(ist).strftime("%Y%m%d_%H%M%S")

    # Save to SQLite DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memories (friend_name, emoji, message, submitted_at)
        VALUES (?, ?, ?, ?)
    """, (name, emoji, message, timestamp))
    conn.commit()
    conn.close()

    # Save local backup text file
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
    filename = f"Memory_{safe_name}_{file_timestamp}.txt"
    filepath = os.path.join(LOCAL_BACKUP_DIR, filename)

    content = f"From: {name}\nMood: {emoji}\nDate: {timestamp}\n\nMessage:\n{message}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def delete_memory(msg_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memories WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()

# ------------------------------------------------------------------------------
# WEBSITE HEADER
# ------------------------------------------------------------------------------
st.title("📖 Vishnu's Farewell Slam Book ✨")
st.markdown("### *College mudinjaachu... enna patri un manasula irukkuradha kottitu podhu!* 💖")
st.write("enna pathi unakku pidichadhu/pidikkadhadhu, best memories... all unfiltered!")

st.divider()

# ------------------------------------------------------------------------------
# FORM TO WRITE A MESSAGE (VISIBLE TO EVERYONE)
# ------------------------------------------------------------------------------
with st.form("memory_form", clear_on_submit=True):
    st.markdown("### 📝 Oru Kutty (or Periya) Message-a Thattu")
    
    friend_name = st.text_input("Yaaru adhu? (Name / Nickname) ✨", placeholder="Type un peru here Bestie...")
    
    selected_emoji = st.selectbox(
        "Namma Gang Vibe Enna? 😎",
        [
            "❤️ Bestie / Paasam", 
            "🎓 Degree Waala", 
            "🔥 Mass-u Vibe", 
            "😂 Sirichu Sethoda (Fun)", 
            "🥳 Party & Gang Vibe", 
            "🌟 Star Friend", 
            "👑 Gang Legend", 
            "🚀 Future Big Shot", 
            "✨ Unforgettable Memories"
        ]
    )
    
    message = st.text_area(
        "Namma Senthu Panna Alapparaiga / Secrets 💬",
        height=250,
        placeholder="Enna Pathi Unakku Thonuradhu / Namma Memory 💬"
    )
    
    words = len(message.split()) if message.strip() else 0
    st.caption(f"Evlo periya essay-um ezhudhalam: **{words:,} words** *(Unlimited)*")
    
    submit_button = st.form_submit_button(" Submit to My Slam Book 🚀", use_container_width=True)

if submit_button:
    if not friend_name.strip():
        st.error("Please enter your name first! 😊")
    elif not message.strip():
        st.error("Please write a message before posting! 💬")
    else:
        chosen_emoji = selected_emoji.split()[0]
        save_memory(friend_name.strip(), chosen_emoji, message.strip())
        
        st.balloons()
        st.success("Thank you so much! Your secret memory has been saved safely! ❤️")
        st.rerun()

st.divider()

# ------------------------------------------------------------------------------
# SIDEBAR ADMIN PANEL & PRIVATE MEMORY WALL
# ------------------------------------------------------------------------------
with st.sidebar:
    st.title("🔒 Admin Access")
    admin_password = st.text_input("Enter Admin Password:", type="password")

if admin_password == ADMIN_PASSWORD:
    st.sidebar.success("🔓 Access Granted!")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, friend_name, emoji, message, submitted_at FROM memories ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    st.markdown("## 👑 Admin Portal - All Posted Memories")
    st.write(f"**Total Secret Memories Received:** `{len(rows)}`")

    if rows:
        for msg_id, name, emoji, msg, time in rows:
            st.markdown(
                f'<div class="memory-card">'
                f'<h3 style="margin: 0; padding-bottom: 5px;">{emoji} <b>{name}</b></h3>'
                f'<p style="font-size: 13px; color: #718096; margin-bottom: 15px;"><i>Posted on {time}</i></p>'
                f'<p style="font-size: 16px; color: #2D3748; white-space: pre-wrap; line-height: 1.6;">{msg}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            if st.button(f"🗑️ Delete Post #{msg_id}", key=f"del_{msg_id}"):
                delete_memory(msg_id)
                st.success(f"Post #{msg_id} deleted!")
                st.rerun()
    else:
        st.info("No memories submitted yet.")

elif admin_password:
    st.sidebar.error("❌ Incorrect Password!")
