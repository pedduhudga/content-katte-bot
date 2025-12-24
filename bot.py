import requests, time, json

TOKEN = "EAAbM7nxGOmABQVZBrZCIUn5vSFaEJP2HBqKB1AzNlTspMgzJPpX7ZC5nV3nuHXL9ZBr8LBZB98TB1ZBMvrpm5khngN2T0bNycOiEZCE5iYyQMJJlw6jICxEFnCOavSOXLxfrwluCqr2m0sHArwz2jvOFUywpNk5VgxZAdqC7uhwq1iE4W6xtUYIJNBj2DfVpnLb8"
BIZ_ID = "17841410513221945"

def bot_loop():
    processed = set()
    while True:
        try:
            with open("insta_db.json", "r") as f: db = json.load(f)
            for pid, config in db.items():
                if config.get('status') != "Active": continue
                url = f"https://graph.facebook.com/v21.0/{pid}/comments?access_token={TOKEN}"
                comments = requests.get(url).json().get('data', [])
                for c in comments:
                    if c['id'] not in processed and config['keyword'] in c.get('text', '').lower():
                        requests.post(f"https://graph.facebook.com/v21.0/{BIZ_ID}/messages", json={
                            "recipient": {"comment_id": c['id']}, "message": {"text": config['message']}, "access_token": TOKEN
                        })
                        db[pid]['count'] += 1
                        with open("insta_db.json", "w") as f: json.dump(db, f)
                        processed.add(c['id'])
        except: pass
        time.sleep(60)

if __name__ == "__main__": bot_loop()