"""Full verification test — run with: python test_all.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.environ['GOOGLE_API_KEY'] = 'test'

print('=== IMPORT CHECK ===')
from tools.report_campaign import report_campaign
from tools.join_campaign import join_campaign
from tools.get_campaign_status import get_campaign_status
from tools.draft_email import draft_email
from tools.verify_fix import verify_fix
print('[OK] All 5 tools import')

from sub_agents.campaign_manager import campaign_manager_agent
from sub_agents.photo_analyzer import photo_analyzer_agent
from sub_agents.email_drafter import email_drafter_agent
from sub_agents.verifier import verifier_agent
print('[OK] All 4 sub-agents import')

from agent import root_agent
print(f'[OK] Orchestrator: {root_agent.name}')
print(f'     Sub-agents: {[a.name for a in root_agent.sub_agents]}')

print()
print('=== TOOL LOGIC TESTS ===')

# 1. Report campaign
r = report_campaign('Broken footpath on Linking Road Bandra', 'Linking Road, Bandra, Mumbai', 'sidewalk', 'W071', 3)
print(f'[report_campaign]  {r["status"]} -> {r.get("campaign_id")} | joins_needed={r.get("joins_still_needed")}')
assert r['status'] == 'created', f'Expected created, got {r["status"]}'
new_id = r['campaign_id']

# 2. Join campaign - progressive joins
j1 = join_campaign(new_id, 'CITIZEN-01')
print(f'[join_campaign #1] {j1["status"]} | count={j1["citizen_count"]} | ready={j1["ready_to_escalate"]}')
assert j1['status'] == 'joined' and j1['citizen_count'] == 2

j2 = join_campaign(new_id, 'CITIZEN-02')
print(f'[join_campaign #2] {j2["status"]} | count={j2["citizen_count"]} | ready={j2["ready_to_escalate"]}')
assert j2['citizen_count'] == 3

jdup = join_campaign(new_id, 'CITIZEN-01')  # duplicate
print(f'[join_campaign dup] {jdup["status"]} (should be already_joined)')
assert jdup['status'] == 'already_joined'

j3 = join_campaign(new_id, 'CITIZEN-03')
print(f'[join_campaign #3] {j3["status"]} | count={j3["citizen_count"]} | ready={j3["ready_to_escalate"]} <- threshold!')
assert j3['ready_to_escalate'] == True

# 3. Get status
s = get_campaign_status(new_id)
print(f'[get_status]       {s["status"]} | count={s["citizen_count"]} | ready={s["ready_to_escalate"]} | sla_days={s["sla_days"]}')
assert s['status'] == 'found'
assert s['ready_to_escalate'] == True

# 4. Threshold block
r2 = report_campaign('Pothole on Carter Road near signal', '123 Carter Road, Mumbai', 'pothole', 'W073', 2)
blocked = draft_email(r2['campaign_id'])
print(f'[draft threshold]  {blocked["status"]} -> {blocked.get("error","")[:70]}')
assert blocked['status'] == 'error'
assert 'join' in blocked['error'].lower()

# 5. Draft email success (CAMP001 has citizen_count=5 >= 3)
ok = draft_email('CAMP001')
print(f'[draft_email OK]   {ok["status"]} -> to={ok.get("to_email")} | draft_id={ok.get("draft_id","")[:8]}')
assert ok['status'] == 'drafted'

# 6. Verify fix - approve path
vr = verify_fix('CAMP003', [
    {'citizen_id': 'C1', 'vote': 'approve', 'reputation': 500},
    {'citizen_id': 'C2', 'vote': 'approve', 'reputation': 300},
    {'citizen_id': 'C3', 'vote': 'reject',  'reputation': 50},
])
print(f'[verify_fix]       approved={vr["approved"]} | rate={vr["approval_rate"]} | status={vr["new_status"]}')
assert vr['approved'] == True

# 7. Verify fix - reject path
vr2 = verify_fix('CAMP002', [
    {'citizen_id': 'C1', 'vote': 'reject', 'reputation': 500},
    {'citizen_id': 'C2', 'vote': 'reject', 'reputation': 300},
])
print(f'[verify_fix]       approved={vr2["approved"]} | rate={vr2["approval_rate"]} | status={vr2["new_status"]}')
assert vr2['approved'] == False

# 8. Input validation edge cases
bad1 = report_campaign('', 'addr', 'pothole', 'W073', 3)
assert bad1['status'] == 'error', 'Empty title should fail'
bad2 = report_campaign('Valid title here ok', 'addr', 'INVALID_TYPE', 'W073', 3)
assert bad2['status'] == 'error', 'Invalid issue_type should fail'
bad3 = report_campaign('Valid title here ok', 'addr', 'pothole', 'BADWARD', 3)
assert bad3['status'] == 'error', 'Bad ward_id should fail'
bad4 = report_campaign('Valid title here ok', 'addr', 'pothole', 'W073', 9)
assert bad4['status'] == 'error', 'Severity 9 should fail'
print('[input_validation] 4/4 edge cases correctly rejected')

print()
print('=== SECURITY CALLBACKS ===')
for a in root_agent.sub_agents:
    cb = getattr(a, 'before_model_callback', None)
    names = [f.__name__ for f in cb] if isinstance(cb, list) else str(cb)
    print(f'  {a.name:22}: {names}')

print()
print('=== ALL 8 TEST GROUPS PASS ===')
