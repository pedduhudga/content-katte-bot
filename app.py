import streamlit as st
import requests
import json
import base64

# --- CREDENTIALS FROM SECRETS ---
TOKEN = "EAAbM7nxGOmABQVZBrZCIUn5vSFaEJP2HBqKB1AzNlTspMgzJPpX7ZC5nV3nuHXL9ZBr8LBZB98TB1ZBMvrpm5khngN2T0bNycOiEZCE5iYyQMJJlw6jICxEFnCOavSOXLxfrwluCqr2m0sHArwz2jvOFUywpNk5VgxZAdqC7uhwq1iE4W6xtUYIJNBj2DfVpnLb8"
BIZ_ID = "17841410513221945"
GH_TOKEN = st.secrets["GITHUB_TOKEN"]
GH_USER = st.secrets["GITHUB_USER"]
GH_REPO = st.secrets["GITHUB_REPO"]
DB_FILE = "insta_db.json"

st.set_page_config(page_title="Content Katte Pro", layout="wide")

# --- GITHUB SYNC FUNCTION ---
def sync_to_github(data):
    url = f"https://api.github.com/repos/{GH_USER}/{GH_REPO}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Get the current file to get its 'sha' (required by GitHub)
    res = requests.get(url, headers=headers).json()
    sha = res.get('sha')
    
    # Convert data to Base64 for GitHub API
    content_bytes = json.dumps(data, indent=4).encode("utf-8")
    content_base64 = base64.b64encode(content_bytes).decode("utf-8")
    
    payload = {
        "message": "Mobile Update",
        "content": content_base64,
        "sha": sha if sha else None
    }
    
    response = requests.put(url, json=payload, headers=headers)
    return response.status_code in [200, 201]

# --- APP INTERFACE ---
st.title("🎬 Content Katte Pro")

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
    tid = st.session_state['active_id']
    st.subheader(f"Setup Reel: {tid}")
    kw = st.text_input("Trigger Keyword:", "link")
    msg = st.text_area("DM Message:")
    
    if st.button("✅ Save & Sync to Bot"):
        # Create the new database entry
        new_db = {tid: {"keyword": kw.lower(), "message": msg, "status": "Active", "count": 0}}
        
        # Sync to GitHub
        if sync_to_github(new_db):
            st.success("🔥 Success! Settings sent to GitHub.")
            st.info("The bot on PythonAnywhere will see this in 60 seconds.")
            del st.session_state['active_id']
        else:
            st.error("Sync Failed. Check your GitHub Token permissions.")
