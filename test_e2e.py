"""Full demo simulation — tests all 7 demo scenarios through the live ADK server"""
import requests, json, sys, time

BASE = "http://127.0.0.1:8000"

def send_message(app_name, user_id, session_id, text):
    """Send a message and collect all events."""
    msg = {
        "app_name": app_name,
        "user_id": user_id,
        "session_id": session_id,
        "new_message": {"role": "user", "parts": [{"text": text}]}
    }
    resp = requests.post(f"{BASE}/run_sse", json=msg, stream=True, timeout=120)
    events = []
    for line in resp.iter_lines():
        if not line:
            continue
        decoded = line.decode("utf-8")
        if not decoded.startswith("data:"):
            continue
        try:
            j = json.loads(decoded[5:])
            author = j.get("author", "")
            for p in j.get("content", {}).get("parts", []):
                txt = p.get("text", "").strip()
                if txt:
                    events.append(("TEXT", author, txt))
                fc = p.get("function_call")
                if fc:
                    events.append(("CALL", author, f"{fc['name']}({json.dumps(fc.get('args',{}))[:120]})"))
                fr = p.get("function_response")
                if fr:
                    events.append(("RESULT", author, json.dumps(fr.get("response", {}))[:200]))
        except json.JSONDecodeError:
            pass
    return events


def run_scenario(num, title, text, app_name, user_id, session_id):
    print(f"\n{'='*60}")
    print(f"  SCENARIO {num}: {title}")
    print(f"{'='*60}")
    print(f"  Message: {text[:100]}...")
    print()
    events = send_message(app_name, user_id, session_id, text)
    for etype, author, content in events:
        tag = f"[{author}]" if author else "[?]"
        prefix = "  " if etype == "TEXT" else "  >> " if etype == "CALL" else "  << "
        print(f"{prefix}{tag} {content[:250]}")
    if not events:
        print("  WARNING: No events received!")
    return events


# ── Setup ──
apps = requests.get(f"{BASE}/list-apps").json()
app_name = apps[0]
print(f"App: {app_name}")

# ── Scenario 1: Report Campaign ──
s = requests.post(f"{BASE}/apps/{app_name}/users/u1/sessions", json={}).json()
run_scenario(1, "Report a New Campaign",
    "Use the report_campaign tool to create a new campaign. Title: Large Pothole on SV Road. "
    "Address: SV Road near Andheri Station Mumbai. issue_type: pothole. ward_id: W073. severity: 4.",
    app_name, "u1", s["id"])
time.sleep(30)  # respect rate limits

# ── Scenario 2: Join Campaign ──
s = requests.post(f"{BASE}/apps/{app_name}/users/u2/sessions", json={}).json()
run_scenario(2, "Join Existing Campaign",
    "Use join_campaign to join campaign CAMP001 with citizen_id CITIZEN-42.",
    app_name, "u2", s["id"])
time.sleep(30)

# ── Scenario 3: Campaign Status ──
s = requests.post(f"{BASE}/apps/{app_name}/users/u3/sessions", json={}).json()
run_scenario(3, "Query Campaign Status",
    "Use get_campaign_status for campaign_id CAMP002.",
    app_name, "u3", s["id"])
time.sleep(30)

# ── Scenario 4: Draft Email ──
s = requests.post(f"{BASE}/apps/{app_name}/users/u4/sessions", json={}).json()
run_scenario(4, "Draft Escalation Email (Threshold Met)",
    "Use draft_email to draft an escalation email for campaign_id CAMP001.",
    app_name, "u4", s["id"])
time.sleep(30)

# ── Scenario 5: Verify Fix ──
s = requests.post(f"{BASE}/apps/{app_name}/users/u5/sessions", json={}).json()
votes_json = json.dumps([
    {"citizen_id": "C001", "vote": "approve", "reputation": 500},
    {"citizen_id": "C002", "vote": "approve", "reputation": 300},
    {"citizen_id": "C003", "vote": "reject", "reputation": 80},
])
run_scenario(5, "Citizen Verification (Weighted Votes)",
    f"Use verify_fix for campaign_id CAMP003 with votes: {votes_json}",
    app_name, "u5", s["id"])
time.sleep(30)

# ── Scenario 6: PII Redaction ──
s = requests.post(f"{BASE}/apps/{app_name}/users/u6/sessions", json={}).json()
run_scenario(6, "Security: PII Redaction",
    "My Aadhaar number is 1234 5678 9012 and my phone is 9876543210. There is garbage on MG Road.",
    app_name, "u6", s["id"])

print(f"\n{'='*60}")
print("  ALL SCENARIOS COMPLETE")
print(f"{'='*60}")
