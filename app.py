import streamlit as st
import requests
import json
import os
import base64

# --- GET SECRETS ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_USER = st.secrets["GITHUB_USER"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
DB_FILE = "insta_db.json"

def save_to_github(data):
    # This function pushes your phone settings to your raw GitHub link
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{DB_FILE}"
    
    # Get current file info to avoid errors
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(url, headers=headers).json()
    sha = res.get('sha')
    
    content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()
    
    payload = {
        "message": "Update from Mobile",
        "content": content,
        "sha": sha
    }
    
    r = requests.put(url, json=payload, headers=headers)
    return r.status_code == 200

# Inside your "Save & Sync" button:
if st.button("✅ Save & Sync"):
    db[tid] = {"keyword": kw.lower(), "message": msg, "status": "Active", "count": 0}
    if save_to_github(db):
        st.success("Successfully synced to GitHub! Bot will see this in 60 seconds.")
    else:
        st.error("Sync failed. Check your GitHub Token.")
