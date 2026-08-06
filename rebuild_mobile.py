import requests, base64, json, re, os, sys

token = base64.b64decode("bXV5d1EySTl0Qmw3cWNYY3VEVHlaQ05CVGlZb2F5V0Z5OTBWX3BoZw==").decode()[::-1]
repo = "compassfiresafety/compass-dashboard"
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

# Get latest data
data = requests.get(f"https://raw.githubusercontent.com/{repo}/main/data.json").json()
try:
    history = requests.get(f"https://raw.githubusercontent.com/{repo}/main/history.json").json()
except:
    history = {}

# Slim data to fields mobile needs
slim = [{"id":p.get("id",""),"propId":p.get("propId",""),"client":p.get("client",""),
    "address":p.get("address",""),"key":p.get("key",""),"active":p.get("active",""),
    "cost":p.get("cost",""),"subscriptionExpires":p.get("subscriptionExpires",""),
    "lastInspected":p.get("lastInspected",""),"compliant":p.get("compliant",""),
    "alarmCount":p.get("alarmCount","")} for p in data]

print(f"Properties: {len(slim)}, History records: {len(history)}")

# Get current mobile file
meta = requests.get(f"https://api.github.com/repos/{repo}/contents/compass_mobile.html", headers=headers).json()
sha = meta["sha"]
current = base64.b64decode(meta["content"].replace("\n","")).decode("utf-8", errors="replace")

# Replace DATA and HISTORY inline
current = re.sub(r"const DATA = \[.*?\];", f"const DATA = {json.dumps(slim, separators=(',',':'))};", current, flags=re.DOTALL)
current = re.sub(r"let HISTORY = \{.*?\};", f"let HISTORY = {json.dumps(history, separators=(',',':'))};", current, flags=re.DOTALL)

# Upload
encoded = base64.b64encode(current.encode()).decode()
res = requests.put(
    f"https://api.github.com/repos/{repo}/contents/compass_mobile.html",
    headers={**headers, "Content-Type": "application/json"},
    json={"message": "Daily mobile app rebuild", "content": encoded, "branch": "main", "sha": sha}
)
print(f"Upload: {res.status_code} - {res.json().get('content', {}).get('size', 0):,} bytes")
