import streamlit as st
import sqlite3
import datetime
import zoneinfo
import os
import base64

# ------------------------------------------------------------------------------
# PAGE CONFIGURATION & PREMIUM STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Vishnu's Slam Book 🎓",
    page_icon="🎓",
    layout="centered"
)

st.markdown("""
    <style>
    /* Premium Soft Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 50%, #A1C4FD 100%) !important;
    }
    
    /* Global Typography - Clean & Modern */
    html, body, [class*="css"], h1, h2, h3, h4, label, p, span, div {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: #1A202C !important;
    }

    /* 🎨 PREMIUM CARD FORM CONTAINER */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        padding: 30px !important;
        border-radius: 24px !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
    }

    /* Form Labels */
    div[data-testid="stForm"] label p {
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #2D3748 !important;
        margin-bottom: 6px !important;
    }

    /* 🎨 INPUT FIELD FIXES (PERU & MESSAGE BOX) */
    .stTextInput input, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
        -webkit-text-fill-color: #1A202C !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        border-radius: 12px !important;
        border: 1.5px solid #E2E8F0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #FF6B6B !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.2) !important;
    }

    /* Placeholders Styling */
    ::placeholder, .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #A0AEC0 !important;
        -webkit-text-fill-color: #A0AEC0 !important;
        font-weight: 400 !important;
    }

    /* 🎨 VIBE DROPDOWN FIX (NO DARK OVERLAY) */
    div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1.5px solid #E2E8F0 !important;
    }

    div[data-baseweb="select"] * {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
        -webkit-text-fill-color: #1A202C !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    ul[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
    }

    ul[data-baseweb="menu"] li {
        color: #1A202C !important;
        background-color: #FFFFFF !important;
    }

    /* 🎨 UPLOAD BOX FIX (NO DUPLICATE ICONS/TEXT) */
    div[data-testid="stFileUploader"] section {
        background-color: #FFFFFF !important;
        border: 2px dashed #CBD5E0 !important;
        border-radius: 16px !important;
        padding: 20px !important;
    }

    div[data-testid="stFileUploader"] section:hover {
        border-color: #FF6B6B !important;
    }

    div[data-testid="stFileUploader"] section button {
        background-color: #EDF2F7 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: #2D3748 !important;
    }

    div[data-testid="stFileUploader"] section * {
        color: #4A5568 !important;
    }

    /* 🚀 SUBMIT BUTTON PREMIUM LOOK */
    div[data-testid="stForm"] button[kind="secondaryFormSubmit"] {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 12px 24px !important;
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
    }

    div[data-testid="stForm"] button[kind="secondaryFormSubmit"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 24px rgba(255, 107, 107, 0.45) !important;
    }

    /* 📖 ADMIN DISPLAY CARDS */
    .memory-card {
        background-color: #FFFFFF !important;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.06);
        margin-bottom: 20px;
        border-left: 6px solid #FF6B6B;
    }

    .memory-card p, .memory-card h3, .memory-card span {
        color: #2D3748 !important;
    }

    /* Delete Container */
    .delete-container {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 16px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        margin-top: 10px;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

DB_PATH = "college_memories.db"
LOCAL_BACKUP_DIR = "drive_backup_memories"

# 🔑 SECRET ADMIN PASSWORD
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
            photo_data TEXT,
            submitted_at TEXT NOT NULL
        )
    """)
    conn.commit()

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

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memories (friend_name, emoji, message, photo_data, submitted_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, emoji, message, photo_b64, timestamp))
    conn.commit()
    conn.close()

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
st.title("🎓 Vishnu's Farewell Slam Book ✨")
st.markdown("##### *College mudinjuchu guys... manasula irukkuradha kottitu podhinga!* 💖")
st.write("Enna pathi unakku thonuradhu, namma memories, secrets... all unfiltered!")

st.divider()

# ------------------------------------------------------------------------------
# FORM TO WRITE A SLAM ENTRY
# ------------------------------------------------------------------------------
with st.form("memory_form", clear_on_submit=True):
    st.markdown("### 📝 Fill My Slam Book!")
    
    friend_name = st.text_input("Yaaru adhu? (Name / Nickname) ✨", placeholder="Type un peru here...")
    
    selected_emoji = st.selectbox(
        "Namma Vibe / Bond Enna? 😎",
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
        "Enna Pathi Unakku Thonuradhu / Namma Memory 💬",
        height=180,
        placeholder="Unakku enna thonudho adha ezhudhu... No limit, fulla thallu! ❤️🥳✨"
    )
    
    uploaded_photo = st.file_uploader("📸 Namma photo edhavathu iruntha podunga (Optional)", type=["jpg", "jpeg", "png"])
    
    words = len(message.split()) if message.strip() else 0
    st.caption(f"Evlo periya essay-um ezhudhalam: **{words:,} words** *(Unlimited)*")
    
    submit_button = st.form_submit_button("Add to Vishnu's Slam Book 🚀", use_container_width=True)

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
            st.markdown(
                f'<div class="memory-card">'
                f'<h3 style="margin: 0; padding-bottom: 5px;">{emoji} <b>{name}</b></h3>'
                f'<p style="font-size: 13px; color: #718096; margin-bottom: 15px;"><i>Posted on {time}</i></p>'
                f'<p style="font-size: 16px; color: #2D3748; white-space: pre-wrap; line-height: 1.6;">{msg}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            if photo_b64:
                try:
                    img_bytes = base64.b64decode(photo_b64)
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
