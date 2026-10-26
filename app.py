import streamlit as st
import sqlite3
import datetime
import zoneinfo
import os
import base64

# ------------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Vishnu's Slam book 🎓",
    page_icon="🎓",
    layout="centered"
)

st.markdown("""
    <style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 50%, #A1C4FD 100%);
    }
    
    /* General Typography Fix */
    h1, h2, h3, h4, label, p, span, div {
        color: #2D3748 !important;
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
    }

    /* 🎨 INPUT BOXES BACKGROUND COLOR FIX (White Background + Dark Text) */
    .stTextInput input, 
    .stTextArea textarea, 
    .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 12px !important;
        border: 1px solid #CBD5E0 !important;
    }

    /* 👁️ PLACEHOLDER TEXT VISIBILITY FIX (Make placeholder text dark & readable) */
    ::placeholder, 
    .stTextInput input::placeholder, 
    .stTextArea textarea::placeholder {
        color: #4A5568 !important;
        -webkit-text-fill-color: #4A5568 !important;
        opacity: 0.85 !important;
    }

    /* Dropdown Selected Text & Options */
    .stSelectbox div[role="button"] {
        background-color: #FFFFFF !important;
        color: #2D3748 !important;
    }

    /* File Uploader Container Fix */
    div[data-testid="stFileUploader"] section {
        background-color: #FFFFFF !important;
        border: 2px dashed #FF6B6B !important;
        border-radius: 15px !important;
    }
    
    div[data-testid="stFileUploader"] section * {
        color: #2D3748 !important;
    }

    /* Form Container Box */
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.45) !important;
        padding: 25px !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
    }

    /* Memory Display Card */
    .memory-card {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 6px solid #FF6B6B;
    }
    .memory-card p, .memory-card h3, .memory-card span {
        color: #2D3748 !important;
    }
    
    /* Delete Confirmation Sub-Box */
    .delete-container {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-top: 10px;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

DB_PATH = "college_memories.db"
LOCAL_BACKUP_DIR = "drive_backup_memories"

# 🔑 YOUR SECRET ADMIN PASSWORD
ADMIN_PASSWORD = "Arovis@191025"

# ------------------------------------------------------------------------------
# DATABASE SETUP WITH AUTO-MIGRATION FIX
# ------------------------------------------------------------------------------
def init_storage():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if not present
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            friend_name TEXT NOT NULL,
            emoji TEXT NOT NULL,
            message TEXT NOT NULL,
            photo_data TEXT,
            submitted_at TEXT NOT NULL
        )
    """)
    conn.commit()

    # Automatically add 'photo_data' column if missing from existing database
    cursor.execute("PRAGMA table_info(memories)")
    columns = [column[1] for column in cursor.fetchall()]
    if "photo_data" not in columns:
        cursor.execute("ALTER TABLE memories ADD COLUMN photo_data TEXT")
        conn.commit()

    conn.close()

    if not os.path.exists(LOCAL_BACKUP_DIR):
        os.makedirs(LOCAL_BACKUP_DIR)

init_storage()

def save_memory(name, emoji, message, photo_b64):
    ist = zoneinfo.ZoneInfo("Asia/Kolkata")
    timestamp = datetime.datetime.now(ist).strftime("%d %B %Y, %I:%M %p")
    file_timestamp = datetime.datetime.now(ist).strftime("%Y%m%d_%H%M%S")

    # Save to SQLite DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memories (friend_name, emoji, message, photo_data, submitted_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, emoji, message, photo_b64, timestamp))
    conn.commit()
    conn.close()

    # Save local backup text file
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
    filename = f"Memory_{safe_name}_{file_timestamp}.txt"
    filepath = os.path.join(LOCAL_BACKUP_DIR, filename)

    content = f"From: {name}\nMood: {emoji}\nDate: {timestamp}\nPhoto Attached: {'Yes' if photo_b64 else 'No'}\n\nMessage:\n{message}"
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
st.title("🎓 Vishnu's Slam Book ✨")
st.markdown("### *College mudinjuchu guys... manasula irukkuradha kottitu podhinga!* 💖")
st.write("Enna Pathi Enna nenachingalo Adha pathi Solunga")

st.divider()

# ------------------------------------------------------------------------------
# FORM TO WRITE A MESSAGE & UPLOAD PHOTO (VISIBLE TO EVERYONE)
# ------------------------------------------------------------------------------
with st.form("memory_form", clear_on_submit=True):
    st.markdown("### 📝 Oru Kutty (or Periya) Message-a Thattu")
    
    friend_name = st.text_input("Yaaru adhu? (Name / Nickname) ✨", placeholder="")
    
    selected_emoji = st.selectbox(
        "Namma Gang Vibe Enna? 😎",
        [
            "❤️ Close Friend / Paasam", 
            "🎓 Degree Vangitom", 
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
        height=200,
        placeholder="Unakku enna thonudho adha ezhudhu... No limit, fulla thallu! ❤️🥳✨"
    )
    
    # 📸 Photo Upload Option
    uploaded_photo = st.file_uploader("📸 Namma photo edhavathu iruntha podunga (Optional)", type=["jpg", "jpeg", "png"])
    
    words = len(message.split()) if message.strip() else 0
    st.caption(f"Evlo periya essay-um ezhudhalam: **{words:,} words** *(Unlimited)*")
    
    submit_button = st.form_submit_button(" Add to Vishnu's Slam book 🚀", use_container_width=True)

if submit_button:
    if not friend_name.strip():
        st.error("Please enter your name first! 😊")
    elif not message.strip() and not uploaded_photo:
        st.error("Please write a message or upload a photo before posting! 💬")
    else:
        chosen_emoji = selected_emoji.split()[0]
        
        photo_b64 = None
        if uploaded_photo is not None:
            photo_bytes = uploaded_photo.read()
            photo_b64 = base64.b64encode(photo_bytes).decode("utf-8")

        save_memory(friend_name.strip(), chosen_emoji, message.strip(), photo_b64)
        
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
    cursor.execute("SELECT id, friend_name, emoji, message, photo_data, submitted_at FROM memories ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    st.markdown("## 👑 Admin Portal - All Posted Memories")
    st.write(f"**Total Secret Memories Received:** `{len(rows)}`")

    if rows:
        for msg_id, name, emoji, msg, photo_b64, time in rows:
            # Memory Card Box
            st.markdown(
                f'<div class="memory-card">'
                f'<h3 style="margin: 0; padding-bottom: 5px;">{emoji} <b>{name}</b></h3>'
                f'<p style="font-size: 13px; color: #718096; margin-bottom: 15px;"><i>Posted on {time}</i></p>'
                f'<p style="font-size: 16px; color: #2D3748; white-space: pre-wrap; line-height: 1.6;">{msg}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            # Display uploaded photo & Save to Gallery button
            if photo_b64:
                try:
                    img_bytes = base64.b64encode(photo_b64)
                    st.image(img_bytes, caption=f"Photo by {name}", use_column_width=True)
                    
                    st.download_button(
                        label=f"📥 Save Photo to Gallery ({name})",
                        data=img_bytes,
                        file_name=f"Farewell_Photo_{name}_{msg_id}.png",
                        mime="image/png",
                        key=f"dl_{msg_id}"
                    )
                except Exception:
                    pass

            # 🛑 DELETE CONFIRMATION CHECKBOX & BUTTON (IN SUB-BOX)
            with st.container():
                st.markdown('<div class="delete-container">', unsafe_allow_html=True)
                confirm_delete = st.checkbox(f"⚠️ Confirm deletion for Post #{msg_id}", key=f"confirm_{msg_id}")
                if st.button(f"🗑️ Delete Post #{msg_id}", key=f"del_{msg_id}"):
                    if confirm_delete:
                        delete_memory(msg_id)
                        st.success(f"Post #{msg_id} deleted successfully!")
                        st.rerun()
                    else:
                        st.warning("Please check the confirmation box above before deleting!")
                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()
    else:
        st.info("No memories submitted yet.")

elif admin_password:
    st.sidebar.error("❌ Incorrect Password!")
