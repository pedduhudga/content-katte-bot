import streamlit as st
import requests
import json
import os

# --- 1. CREDENTIALS & DB SETUP ---
TOKEN = "EAAbM7nxGOmABQVZBrZCIUn5vSFaEJP2HBqKB1AzNlTspMgzJPpX7ZC5nV3nuHXL9ZBr8LBZB98TB1ZBMvrpm5khngN2T0bNycOiEZCE5iYyQMJJlw6jICxEFnCOavSOXLxfrwluCqr2m0sHArwz2jvOFUywpNk5VgxZAdqC7uhwq1iE4W6xtUYIJNBj2DfVpnLb8"
BIZ_ID = "17841410513221945"
DB_FILE = "insta_db.json"

st.set_page_config(page_title="Content Katte Pro", layout="wide")

def load_db():
    if not os.path.exists(DB_FILE):
        # Create file if it doesn't exist
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

# --- 2. HEADER & SEARCH ---
st.title("🎬 Content Katte Pro Manager")

# Reset button to go back to the gallery
if st.button("🔄 Refresh / Home"):
    if 'active_id' in st.session_state:
        del st.session_state['active_id']
    st.rerun()

search_query = st.text_input("🔍 Search Reels/Posts by caption:", "").lower()

# --- 3. FETCH FEED ---
@st.cache_data(ttl=300)
def fetch_feed():
    url = f"https://graph.facebook.com/v21.0/{BIZ_ID}/media?fields=id,caption,thumbnail_url,media_url&access_token={TOKEN}"
    try:
        r = requests.get(url).json()
        return r.get('data', [])
    except:
        return []

feed = fetch_feed()
filtered_feed = [i for i in feed if search_query in i.get('caption', '').lower()]

# --- 4. THE GALLERY GRID ---
# Only show gallery if no specific reel is being edited
if 'active_id' not in st.session_state:
    st.subheader(f"Showing {len(filtered_feed)} posts")
    cols = st.columns(3) # Better for mobile than 4 columns
    
    for i, item in enumerate(filtered_feed):
        pid = item['id']
        with cols[i % 3]:
            with st.container(border=True):
                img_url = item.get('thumbnail_url') or item.get('media_url')
                st.image(img_url, use_container_width=True)
                
                # Show status badge
                if pid in db:
                    status = db[pid].get('status', 'Stopped')
                    count = db[pid].get('count', 0)
                    st.success(f"✅ {status} | Sent: {count}")
                    
                    if st.button("Manage Settings", key=f"btn_{pid}", use_container_width=True):
                        st.session_state['active_id'] = pid
                        st.rerun()
                else:
                    if st.button("➕ Automate", key=f"btn_{pid}", use_container_width=True):
                        st.session_state['active_id'] = pid
                        st.rerun()

# --- 5. THE SETTINGS EDITOR (Appears when button is clicked) ---
else:
    target_id = st.session_state['active_id']
    st.divider()
    st.header(f"🛠️ Settings for Reel: {target_id}")
    
    # Get current settings if they exist
    current_data = db.get(target_id, {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        keyword = st.text_input("Trigger Keyword (e.g., link):", value=current_data.get('keyword', 'link'))
        message = st.text_area("DM Message to send:", value=current_data.get('message', ''))
        
    with col2:
        st.write("**Change Status**")
        c1, c2, c3 = st.columns(3)
        
        if c1.button("▶️ Active"):
            db.setdefault(target_id, {})['status'] = "Active"
            st.toast("Set to Active")
            
        if c2.button("⏸️ Pause"):
            db.setdefault(target_id, {})['status'] = "Paused"
            st.toast("Paused")
            
        if c3.button("⏹️ Stop"):
            db.setdefault(target_id, {})['status'] = "Stopped"
            st.toast("Stopped")

    st.divider()
    
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    if btn_col1.button("✅ Save & Update", use_container_width=True):
        if target_id not in db:
            db[target_id] = {"count": 0, "status": "Active"}
        
        db[target_id].update({
            "keyword": keyword.lower().strip(),
            "message": message
        })
        save_db(db)
        st.success("Settings Saved Successfully!")
        # Clear selection and go back to home
        del st.session_state['active_id']
        st.rerun()
        
    if btn_col2.button("🗑️ Delete Automation", use_container_width=True):
        if target_id in db:
            del db[target_id]
            save_db(db)
        del st.session_state['active_id']
        st.rerun()

    if btn_col3.button("🔙 Back to Gallery", use_container_width=True):
        del st.session_state['active_id']
        st.rerun()
