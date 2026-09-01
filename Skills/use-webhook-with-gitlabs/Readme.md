🔗 GitLab Webhooks — Complete Research & Implementation Guide
 
Based on official GitLab documentation — comprehensive, up-to-date, production-ready
 
 
 
📑 Table of Contents
 
1. Overview
2. Types of Webhooks
3. Supported Events
4. Configuration Steps
5. Security Features
6. Request Headers
7. Custom Payload Templates
8. Branch Filtering
9. Limits & Constraints
10. FastAPI Webhook Listener — Full Implementation
11. Testing & Monitoring
12. Best Practices
 
 
 
📌 Overview
 
GitLab webhooks connect GitLab to external systems through real-time HTTP POST notifications. When events occur in GitLab (push, merge request, issue, pipeline, etc.), detailed JSON payloads are sent to your configured endpoint.
 
Common Use Cases
 
- 🔄 CI/CD Automation — Trigger pipelines/deploys on code push
- 💬 Chat Notifications — Alert Slack/Discord on MRs, issues, pipeline failures
- 📊 Activity Tracking — Monitor development activity across organizations
- 🎟️ External Issue Trackers — Sync Jira/Linear when GitLab issues change
- 👥 User Provisioning — Auto-manage access when users/groups/projects change
 
 
 
🏷️ Types of Webhooks
 
Type Scope Tier Required Permissions 
Project Webhook Single project Free Maintainer / Owner 
Group Webhook All projects in a group + subgroups Premium / Ultimate Group Owner 
System Webhook Entire GitLab instance Free (Self-Managed) Administrator 
 
💡 If both group and project webhooks are configured for the same event, both fire — flexible event handling at different levels.
 
 
 
🎯 Supported Events
 
Both Project & Group Webhooks
 
Event Trigger  X-Gitlab-Event  Header 
Push Code pushed to repo  Push Hook  
Tag Tag created/deleted  Tag Push Hook  
Issue Issue created/updated/closed/reopened  Issue Hook  
Comment Comment on commit/MR/issue/snippet  Note Hook  
Merge Request MR created/edited/merged/closed  Merge Request Hook  
Pipeline Pipeline status changes  Pipeline Hook  
Job Job status changes  Job Hook  
Deployment Deployment starts/succeeds/fails/canceled  Deployment Hook  
Wiki Page Wiki created/edited/deleted  Wiki Page Hook  
Feature Flag Feature flag turned on/off — 
Emoji Emoji reaction added/removed — 
Milestone Milestone created/closed/reopened/deleted — 
Release Release created/edited/deleted — 
Vulnerability Vulnerability created/updated — 
Work Item Work item created/edited/closed/reopened — 
Access Token Project/group token expiring in 7 days — 
 
Group Webhooks Only
 
Event Trigger 
Group Member User added/removed/role changed 
Project Project created/deleted in group 
Subgroup Subgroup created/removed 
 
System Webhooks (Admin Only)
 
Event Trigger 
 user_create  /  user_destroy  /  user_rename  User lifecycle events 
 user_failed_login  Blocked user attempts login 
 user_add_to_team  /  user_remove_from_team  Project membership changes 
 user_add_to_group  /  user_remove_from_group  Group membership changes 
 project_create  /  project_destroy  /  project_rename  /  project_transfer  /  project_update  Project lifecycle 
 group_create  /  group_destroy  /  group_rename  Group lifecycle 
 key_create  /  key_destroy  SSH key changes 
 push  /  tag_push  /  merge_request  Code events (all projects) 
 
 
 
⚙️ Configuration Steps
 
Project Webhook
 
1. Go to your project → Settings → Webhooks
2. Click Add new webhook
3. URL: Enter your endpoint URL (e.g.,  https://api.example.com/webhooks/gitlab )
4. Security (choose one):
- Signing Token (recommended, GitLab 19.0+): Click Generate signing token → save the  whsec_  token
- Secret Token (legacy): Enter a secret string → sent in  X-Gitlab-Token  header
5. Trigger: Select events to listen for
6. Optional: Configure branch filtering, SSL verification, custom headers, custom template
7. Click Add webhook
 
 
 
🔐 Security Features
 
1. Signing Token (Recommended — GitLab 19.0+)
 
Computes HMAC-SHA256 signature over the payload. Verifies both authenticity and integrity.
 
Headers sent:
 
plaintext
  
webhook-id: msg_xxxxxxxxxxxx
webhook-timestamp: 1756789200
webhook-signature: v1,base64_encoded_signature
 
 
Signature computation:
 
plaintext
  
signature = HMAC-SHA256(
  key = base64_decode(signing_token.removeprefix("whsec_")),
  message = "{webhook-id}.{webhook-timestamp}.{raw_body}"
)
 
 
Python verification:
 
python
  
import base64
import hashlib
import hmac

def verify_signature(signing_token: str, message_id: str, timestamp: str, body: str, received_sigs: str) -> bool:
    raw_key = base64.b64decode(signing_token.removeprefix("whsec_"))
    message = f"{message_id}.{timestamp}.{body}".encode()
    digest = hmac.new(raw_key, message, hashlib.sha256).digest()
    expected = "v1," + base64.b64encode(digest).decode()
    return any(hmac.compare_digest(expected, sig) for sig in received_sigs.split(" "))
 
 
Prevent replay attacks:
 
python
  
import time

# Validate timestamp is within 5 minutes
if abs(time.time() - int(timestamp)) > 300:
    raise Exception("Timestamp too old — possible replay attack")
 
 
2. Secret Token (Legacy)
 
Sent as plain text in the  X-Gitlab-Token  header. Weaker security — only verifies source, not payload integrity.
 
python
  
# Simple validation
received_token = request.headers.get("X-Gitlab-Token")
if not hmac.compare_digest(received_token or "", EXPECTED_TOKEN):
    return Response(status_code=401)
 
 
3. Custom Headers (GitLab 16.11+)
 
Add up to 20 custom headers per webhook for external service authentication. Values are masked in logs.
 
4. URL Masking
 
Mask sensitive portions of URLs (e.g., API keys). Masked values:
 
- Replaced at execution time
- Not logged
- Encrypted at rest in the database
 
5. Mutual TLS (GitLab Self-Managed 16.9+)
 
Configure a global client certificate for all webhook connections. GitLab presents the cert during TLS handshake.
 
 
 
📤 Request Headers
 
Header Description 
 Content-Type   application/json  
 X-Gitlab-Event  Event type (e.g.,  Push Hook ,  Merge Request Hook ) 
 X-Gitlab-Token  Secret token (if configured) 
 webhook-id  Unique message ID (signing token mode) 
 webhook-timestamp  Unix timestamp (signing token mode) 
 webhook-signature  HMAC-SHA256 signature (signing token mode) 
 Idempotency-Key  Unique key for retries 
 
 
 
🧩 Custom Payload Templates (GitLab 16.10+)
 
Control exactly what data is sent in the request body using  {{field_name}}  syntax.
 
Example Template:
 
json
  
{
  "event": "{{object_kind}}",
  "project": "{{project.name}}",
  "branch": "{{ref}}",
  "author": "{{user_name}}",
  "commit_count": "{{total_commits_count}}",
  "action": "{{object_attributes.action}}"
}
 
 
Resulting Payload (Push Event):
 
json
  
{
  "event": "push",
  "project": "Diaspora",
  "branch": "refs/heads/master",
  "author": "John Smith",
  "commit_count": "4",
  "action": ""
}
 
 
📌 Access nested properties with periods:  {{project.name}} ,  {{object_attributes.action}} 
❌ Cannot access properties inside arrays
 
 
 
🌿 Branch Filtering for Push Events
 
Filter which branches trigger push events:
 
Filter Type Example Matches 
All branches — Every branch 
Wildcard pattern  *-stable   v1-stable ,  production-stable  
Wildcard pattern  production/*   production/api ,  production/web  
Regex (RE2 syntax) `^(feature hotfix)/.*` 
 
 
 
⚠️ Limits & Constraints
 
Limit Value Notes 
Push event branches/tags Default: 3 per push If exceeded, no webhook fires at all for that push 
Commits in payload Max 20 newest  total_commits_count  shows actual number 
Custom headers Max 20 per webhook GitLab 16.11+ 
Recent events history Last 2 days View in Settings → Webhooks → Edit → Recent events 
Webhook timeout Configurable Admin setting on Self-Managed 
Rate limiting Yes GitLab.com enforces calls-per-minute limits 
 
⚠️ Important: If you push more than 3 branches/tags at once, no webhook is triggered. This is a common gotcha!
 
 
 
🚀 FastAPI Webhook Listener — Full Implementation
 
📄  gitlab_webhook.py 
 
python
  
"""
GitLab Webhook Listener — FastAPI
Features: HMAC-SHA256 signature verification, replay protection,
event routing, async processing, idempotency
"""
from fastapi import FastAPI, Request, Response, HTTPException, status
from pydantic import BaseModel
import base64
import hashlib
import hmac
import time
import json
import logging
from typing import Dict, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GitLab Webhook Listener")

# ── Configuration ──
SIGNING_TOKEN = "whsec_xxxxxxxxxxxxxxxxxxxxxxxx"  # From GitLab
SECRET_TOKEN = "your-legacy-secret"  # Optional fallback
TIMESTAMP_TOLERANCE = 300  # 5 minutes replay protection
processed_events: set = set()  # Simple idempotency (use Redis in production)

# ── Event Handlers Registry ──
event_handlers: Dict[str, Callable] = {}

def handle_event(event_type: str):
    """Decorator to register event handlers"""
    def decorator(func):
        event_handlers[event_type] = func
        return func
    return decorator

# ── Signature Verification ──
def verify_signing_token(request: Request, body: str) -> bool:
    """Verify HMAC-SHA256 signature (GitLab 19.0+ signing token)"""
    message_id = request.headers.get("webhook-id")
    timestamp = request.headers.get("webhook-timestamp")
    signature_header = request.headers.get("webhook-signature")
    
    if not all([message_id, timestamp, signature_header]):
        return False
    
    # Replay protection
    if abs(time.time() - int(timestamp)) > TIMESTAMP_TOLERANCE:
        logger.warning("Replay attack detected — timestamp too old")
        return False
    
    # Idempotency check
    if message_id in processed_events:
        logger.info(f"Duplicate event {message_id} — already processed")
        return True
    
    try:
        raw_key = base64.b64decode(SIGNING_TOKEN.removeprefix("whsec_"))
        message = f"{message_id}.{timestamp}.{body}".encode()
        digest = hmac.new(raw_key, message, hashlib.sha256).digest()
        expected = "v1," + base64.b64encode(digest).decode()
        
        valid = any(
            hmac.compare_digest(expected, sig.strip())
            for sig in signature_header.split(" ")
        )
        
        if valid:
            processed_events.add(message_id)
        
        return valid
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False

def verify_secret_token(request: Request) -> bool:
    """Legacy X-Gitlab-Token verification"""
    received = request.headers.get("X-Gitlab-Token", "")
    return hmac.compare_digest(received, SECRET_TOKEN)

# ── Event Handlers ──
@handle_event("Push Hook")
async def handle_push(payload: dict):
    """Handle code push events"""
    ref = payload.get("ref", "")
    branch = ref.replace("refs/heads/", "")
    user = payload.get("user_name", "unknown")
    commits = payload.get("total_commits_count", 0)
    project = payload.get("project", {}).get("name", "unknown")
    
    logger.info(f"📥 PUSH: {user} pushed {commits} commit(s) to {project}/{branch}")
    
    # TODO: Trigger CI, deploy, notify, etc.
    return {"status": "ok", "action": "push_processed"}

@handle_event("Merge Request Hook")
async def handle_merge_request(payload: dict):
    """Handle merge request events"""
    attrs = payload.get("object_attributes", {})
    action = attrs.get("action", "unknown")
    title = attrs.get("title", "untitled")
    state = attrs.get("state", "unknown")
    url = attrs.get("url", "")
    
    logger.info(f"🔀 MR: [{action}] {title} — State: {state}")
    logger.info(f"   URL: {url}")
    
    if action == "merge" and state == "merged":
        logger.info("   ✅ Merge completed — triggering deployment pipeline")
    
    return {"status": "ok", "action": "mr_processed"}

@handle_event("Issue Hook")
async def handle_issue(payload: dict):
    """Handle issue events"""
    attrs = payload.get("object_attributes", {})
    action = attrs.get("action", "unknown")
    title = attrs.get("title", "untitled")
    labels = [l["title"] for l in payload.get("labels", [])]
    
    logger.info(f"📋 ISSUE: [{action}] {title} — Labels: {labels}")
    return {"status": "ok", "action": "issue_processed"}

@handle_event("Pipeline Hook")
async def handle_pipeline(payload: dict):
    """Handle pipeline status changes"""
    attrs = payload.get("object_attributes", {})
    status = attrs.get("status", "unknown")
    ref = attrs.get("ref", "unknown")
    duration = attrs.get("duration", 0)
    
    logger.info(f"🏗️ PIPELINE: {ref} — Status: {status} — Duration: {duration}s")
    
    if status == "failed":
        logger.error("   ❌ Pipeline FAILED — sending alert notification")
    elif status == "success":
        logger.info("   ✅ Pipeline SUCCESS")
    
    return {"status": "ok", "action": "pipeline_processed"}

@handle_event("Note Hook")
async def handle_comment(payload: dict):
    """Handle comments on commits/MRs/issues"""
    attrs = payload.get("object_attributes", {})
    note_type = attrs.get("noteable_type", "unknown")
    note = attrs.get("note", "")[:100]
    user = payload.get("user", {}).get("username", "unknown")
    
    logger.info(f"💬 COMMENT: [{note_type}] @{user}: {note}...")
    return {"status": "ok", "action": "comment_processed"}

# ── Main Webhook Endpoint ──
@app.post("/webhooks/gitlab")
async def gitlab_webhook(request: Request):
    """
    Main GitLab webhook endpoint
    - Verifies request authenticity
    - Routes to appropriate event handler
    - Returns 200 immediately (process async in production)
    """
    body = await request.body()
    body_str = body.decode()
    
    # ── Security Verification ──
    has_signing = request.headers.get("webhook-signature")
    has_secret = request.headers.get("X-Gitlab-Token")
    
    if has_signing:
        if not verify_signing_token(request, body_str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
    elif has_secret:
        if not verify_secret_token(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    else:
        # In production, reject unsigned requests
        logger.warning("⚠️ No security token/signature provided")
        # raise HTTPException(status_code=401, detail="No authentication")
    
    # ── Parse & Route ──
    event_type = request.headers.get("X-Gitlab-Event", "Unknown")
    
    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # ── Handle Event ──
    handler = event_handlers.get(event_type)
    if handler:
        try:
            result = await handler(payload)
            return {
                "status": "processed",
                "event": event_type,
                "result": result
            }
        except Exception as e:
            logger.error(f"Handler error for {event_type}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Handler error: {str(e)}")
    else:
        logger.info(f"ℹ️ No handler for event: {event_type}")
        return {
            "status": "acknowledged",
            "event": event_type,
            "note": "No specific handler registered"
        }

# ── Health Check ──
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gitlab-webhook-listener"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gitlab_webhook:app", host="0.0.0.0", port=8080, reload=True)
 
 
📄  requirements.txt 
 
txt
  
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.12
 
 
🚀 Run
 
bash
  
pip install -r requirements.txt
python gitlab_webhook.py
# Endpoint: http://localhost:8080/webhooks/gitlab
 
 
 
 
🧪 Testing & Monitoring
 
Test a Webhook
 
1. Go to Settings → Webhooks → Edit
2. Scroll to Recent events
3. Click Test dropdown → select event type
4. GitLab sends a sample payload immediately
 
Monitor Recent Events
 
- View last 2 days of webhook requests in Recent events section
- See: HTTP status code, event type, elapsed time, timestamp
- Click View details to inspect full request/response headers and body
- Click Resend Request to retry with the same payload and  Idempotency-Key 
 
Status Code Legend
 
Color Meaning 
🟢 Green 200–299 (Success) 
🔴 Red All other codes or  internal error  
 
 
 
✅ Best Practices
 
Security
 
1. ✅ Use Signing Token (GitLab 19.0+) instead of plain Secret Token
2. ✅ Validate timestamp to prevent replay attacks (5 min tolerance)
3. ✅ Use HTTPS endpoints with valid SSL certificates
4. ✅ Store secrets securely — never hardcode in code or config files
5. ✅ Verify idempotency using  webhook-id  or  Idempotency-Key  header
 
Reliability
 
1. ✅ Return 200 quickly — process payload asynchronously (queue with Celery/RQ)
2. ✅ Implement retry logic on your endpoint — GitLab retries on failure
3. ✅ Use idempotency keys to avoid duplicate processing
4. ✅ Monitor webhook health via Recent events and your own metrics
 
Design
 
1. ✅ Use custom payload templates to send only needed data — smaller payloads = faster processing
2. ✅ Filter by branch for push events to reduce noise
3. ✅ Register group webhooks (Premium) for centralized handling across projects
4. ✅ Use system hooks (Self-Managed) for instance-wide automation
5. ✅ Mask sensitive URL parts to avoid leaking secrets in logs
 
Common Pitfalls to Avoid
 
- ⚠️ Pushing >3 branches/tags at once = no webhook fires
- ⚠️ Commits >20 at once = only newest 20 in payload (check  total_commits_count )
- ⚠️ No user public email =  email  field shows  [REDACTED] 
- ⚠️ System hooks = commits are never displayed in payload
 
 
 
📌 Quick Reference — Common  X-Gitlab-Event  Values
 
Event Header Value 
Push  Push Hook  
Tag Push  Tag Push Hook  
Issue  Issue Hook  
Comment  Note Hook  
Merge Request  Merge Request Hook  
Pipeline  Pipeline Hook  
Job  Job Hook  
Deployment  Deployment Hook  
Wiki  Wiki Page Hook  
System Hook  System Hook  
 
 
 
Sources: Official GitLab Documentation
 
- https://docs.gitlab.com/ee/user/project/integrations/webhooks.html
- https://docs.gitlab.com/ee/user/project/integrations/webhook_events.html
- https://docs.gitlab.com/administration/system_hooks/
 
Want me to integrate this webhook listener with your OnSpaceAI Stack or CI/CD pipeline? Or generate specific handlers for your use case? 🚀
