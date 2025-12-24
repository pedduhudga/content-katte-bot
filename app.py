import streamlit as st
import requests
import json
import base64

# --- 1. CONFIG & SECRETS ---
# Using your new token provided
TOKEN = "EAAbM7nxGOmABQSSOWrscFznzbZBQnva0BkvJuX9qNzbPi2kX7VzDzCZBzGcPbktx1EM0tgPiZAkr7fFSphilcj1wZCWZBZA9OpTeZAsHr6jC3wvD5H00TLAmjowHVVcirZAZAvEWFe8WwLb7xufqwhElGifW9g5ePgPGB2MaxZBZAcZAhPiDvETTOnDUjkVcKhrE4QSBJKwIsZC2T80LEWnw7VMRWSv3faCqDoxbXJUqbzCltZBYxn5pNno1BkTybeRXQKkhaZCkZABczBjoMYwG3uWYx5zc"
BIZ_ID = "17841410513221945"
GH_RAW_URL = "https://raw.githubusercontent.com/pedduhudga/content-katte-bot/main/insta_db.json"
GH_TOKEN = st.secrets["GITHUB_TOKEN"]
GH_USER = st.secrets["GITHUB_USER"]
GH_REPO = st.secrets["GITHUB_REPO"]
DB_FILE = "insta_db.json"

st.set_page_config(page_title="Content Katte Pro", layout="wide")

def load_db():
    try:
        r = requests.get(GH_RAW_URL)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def sync_to_github(data):
    url = f"https://api.github.com/repos/{GH_USER}/{GH_REPO}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers).json()
    sha = res.get('sha')
    content_base64 = base64.b64encode(json.dumps(data, indent=4).encode("utf-8")).decode("utf-8")
    payload = {"message": "Update Automation", "content": content_base64, "sha": sha if sha else None}
    return requests.put(url, json=payload, headers=headers).status_code in [200, 201]

if 'db' not in st.session_state:
    st.session_state['db'] = load_db()
db = st.session_state['db']

st.title("🎬 Content Katte Pro")

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
            if pid in db: st.success(f"✅ Active: {db[pid]['keyword']}")
            if st.button("Manage" if pid in db else "Automate", key=pid):
                st.session_state['active_id'] = pid
                st.rerun()
else:
    tid = st.session_state['active_id']
    st.subheader(f"Setup Reel: {tid}")
    kw = st.text_input("Trigger Keyword:", value=db.get(tid, {}).get('keyword', 'link'))
    msg = st.text_area("DM Message:", value=db.get(tid, {}).get('message', ''))
    
    if st.button("✅ Save & Sync to Bot"):
        db[tid] = {"keyword": kw.lower(), "message": msg, "status": "Active", "count": 0}
        if sync_to_github(db):
            st.success("Synced to GitHub!")
            st.session_state['db'] = db
            del st.session_state['active_id']
            st.rerun()
    if st.button("🔙 Back"):
        del st.session_state['active_id']
        st.rerun()
