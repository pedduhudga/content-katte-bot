import streamlit as st
import requests
import json
import os

# --- CREDENTIALS ---
TOKEN = "EAAbM7nxGOmABQVZBrZCIUn5vSFaEJP2HBqKB1AzNlTspMgzJPpX7ZC5nV3nuHXL9ZBr8LBZB98TB1ZBMvrpm5khngN2T0bNycOiEZCE5iYyQMJJlw6jICxEFnCOavSOXLxfrwluCqr2m0sHArwz2jvOFUywpNk5VgxZAdqC7uhwq1iE4W6xtUYIJNBj2DfVpnLb8"
BIZ_ID = "17841410513221945"
DB_FILE = "insta_db.json"

st.set_page_config(page_title="Content Katte Pro", layout="wide")

def load_db():
    if not os.path.exists(DB_FILE): return {}
    with open(DB_FILE, "r") as f:
        try: return json.load(f)
        except: return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

st.title("🎬 Content Katte Pro")

# --- FEED SECTION ---
@st.cache_data(ttl=300)
def fetch_feed():
    url = f"https://graph.facebook.com/v21.0/{BIZ_ID}/media?fields=id,caption,thumbnail_url,media_url&access_token={TOKEN}"
    return requests.get(url).json().get('data', [])

if 'active_id' not in st.session_state:
    feed = fetch_feed()
    cols = st.columns(3)
    for i, item in enumerate(feed):
        with cols[i % 3]:
            st.image(item.get('thumbnail_url') or item.get('media_url'))
            if st.button("Automate", key=item['id']):
                st.session_state['active_id'] = item['id']
                st.rerun()
else:
    # --- EDITOR SECTION ---
    tid = st.session_state['active_id']
    st.subheader(f"Settings for Reel: {tid}")
    kw = st.text_input("Keyword:", value=db.get(tid, {}).get('keyword', 'link'))
    msg = st.text_area("Message:", value=db.get(tid, {}).get('message', ''))
    
    if st.button("✅ Save & Sync"):
        db[tid] = {"keyword": kw.lower(), "message": msg, "status": "Active", "count": 0}
        save_db(db)
        st.success("Saved! Now the bot will see this Reel ID automatically.")
        del st.session_state['active_id']
        st.rerun()
    
    if st.button("🔙 Back"):
        del st.session_state['active_id']
        st.rerun()
