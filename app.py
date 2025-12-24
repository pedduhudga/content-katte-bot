import streamlit as st
import requests
import json
import base64

# --- 1. CONFIG & SECRETS ---
TOKEN = "EAAbM7nxGOmABQVZBrZCIUn5vSFaEJP2HBqKB1AzNlTspMgzJPpX7ZC5nV3nuHXL9ZBr8LBZB98TB1ZBMvrpm5khngN2T0bNycOiEZCE5iYyQMJJlw6jICxEFnCOavSOXLxfrwluCqr2m0sHArwz2jvOFUywpNk5VgxZAdqC7uhwq1iE4W6xtUYIJNBj2DfVpnLb8"
BIZ_ID = "17841410513221945"
GH_RAW_URL = "https://raw.githubusercontent.com/pedduhudga/content-katte-bot/main/insta_db.json"
GH_TOKEN = st.secrets["GITHUB_TOKEN"]
GH_USER = st.secrets["GITHUB_USER"]
GH_REPO = st.secrets["GITHUB_REPO"]
DB_FILE = "insta_db.json"

st.set_page_config(page_title="Content Katte Pro", layout="wide")

# --- 2. SYNC FUNCTIONS ---
def load_db():
    try:
        r = requests.get(GH_RAW_URL)
        if r.status_code == 200:
            return r.json()
    except:
        return {}
    return {}

def sync_to_github(data):
    url = f"https://api.github.com/repos/{GH_USER}/{GH_REPO}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers).json()
    sha = res.get('sha')
    content_bytes = json.dumps(data, indent=4).encode("utf-8")
    content_base64 = base64.b64encode(content_bytes).decode("utf-8")
    payload = {"message": "Mobile Update", "content": content_base64, "sha": sha if sha else None}
    response = requests.put(url, json=payload, headers=headers)
    return response.status_code in [200, 201]

# Load database into session state if not already there
if 'db' not in st.session_state:
    st.session_state['db'] = load_db()

db = st.session_state['db']

# --- 3. APP UI ---
st.title("🎬 Content Katte Pro")

if st.button("🔄 Refresh Data"):
    st.session_state['db'] = load_db()
    st.rerun()

@st.cache_data(ttl=300)
def fetch_feed():
    url = f"https://graph.facebook.com/v21.0/{BIZ_ID}/media?fields=id,caption,thumbnail_url,media_url&access_token={TOKEN}"
    return requests.get(url).json().get('data', [])

if 'active_id' not in st.session_state:
    feed = fetch_feed()
    cols = st.columns(3)
    for i, item in enumerate(feed):
        pid = item['id']
        with cols[i % 3]:
            st.image(item.get('thumbnail_url') or item.get('media_url'))
            # Show if reel is already automated
            if pid in db:
                st.success(f"✅ Active: {db[pid]['keyword']}")
            
            if st.button("Manage" if pid in db else "Automate", key=pid):
                st.session_state['active_id'] = pid
                st.rerun()
else:
    # EDITOR
    tid = st.session_state['active_id']
    st.subheader(f"Setup Reel: {tid}")
    
    # Pre-fill data from DB if it exists
    current_kw = db.get(tid, {}).get('keyword', 'link')
    current_msg = db.get(tid, {}).get('message', '')
    
    kw = st.text_input("Trigger Keyword:", value=current_kw)
    msg = st.text_area("DM Message:", value=current_msg)
    
    if st.button("✅ Save & Sync to Bot"):
        db[tid] = {"keyword": kw.lower(), "message": msg, "status": "Active", "count": 0}
        if sync_to_github(db):
            st.success("Synced to Cloud!")
            st.session_state['db'] = db
            del st.session_state['active_id']
            st.rerun()
            
    if st.button("🔙 Back"):
        del st.session_state['active_id']
        st.rerun()
