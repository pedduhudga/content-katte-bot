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
    with open(DB_FILE, "r") as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

db = load_db()

st.title("🎬 Content Katte Pro Manager")

# --- 1. DASHBOARD OVERVIEW ---
if db:
    st.divider()
    st.subheader("📊 Performance Overview")
    total_dms = sum(p.get('count', 0) for p in db.values())
    active_count = sum(1 for p in db.values() if p.get('status') == 'Active')
    
    m1, m2 = st.columns(2)
    m1.metric("Total DMs Sent", total_dms)
    m2.metric("Active Campaigns", active_count)
    
    kw_stats = {p['keyword']: kw_stats.get(p['keyword'], 0) + p.get('count', 0) for p in db.values()}
    if kw_stats: st.bar_chart(kw_stats)
    st.divider()

# --- 2. SEARCH & SELECTION ---
search_query = st.text_input("🔍 Search Reels/Posts:", placeholder="Search captions...")

@st.cache_data(ttl=300)
def fetch_feed():
    url = f"https://graph.facebook.com/v21.0/{BIZ_ID}/media?fields=id,caption,thumbnail_url,media_url&access_token={TOKEN}"
    return requests.get(url).json().get('data', [])

feed = fetch_feed()
filtered = [i for i in feed if search_query.lower() in i.get('caption', '').lower()]

cols = st.columns(3)
for i, item in enumerate(filtered):
    with cols[i % 3]:
        with st.container(border=True):
            st.image(item.get('thumbnail_url') or item.get('media_url'))
            pid = item['id']
            if pid in db:
                st.caption(f"Status: {db[pid]['status']} | Sent: {db[pid]['count']}")
                if st.button("Manage", key=f"m_{pid}"): st.session_state['active_id'] = pid
            else:
                if st.button("Automate", key=f"a_{pid}"): st.session_state['active_id'] = pid

# --- 3. EDITOR ---
if 'active_id' in st.session_state:
    tid = st.session_state['active_id']
    st.divider()
    st.write(f"### Settings for: {tid}")
    new_kw = st.text_input("Keyword:", value=db.get(tid, {}).get('keyword', 'link'))
    new_dm = st.text_area("DM Message:", value=db.get(tid, {}).get('message', ''))
    
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("▶️ Start"): db.setdefault(tid, {})['status'] = "Active"
    if c2.button("⏸️ Pause"): db.setdefault(tid, {})['status'] = "Paused"
    if c3.button("⏹️ Stop"): db.setdefault(tid, {})['status'] = "Stopped"
    if c4.button("✅ Save"):
        db[tid].update({"keyword": new_kw.lower(), "message": new_dm})
        if 'count' not in db[tid]: db[tid]['count'] = 0
        save_db(db); st.rerun()