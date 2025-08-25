import os
import requests
from django.utils import timezone
from .models import FeedActivity


# CONFIG: update these values or keep the provided ones
LINKEDIN_API_HOST = "fresh-linkedin-scraper-api.p.rapidapi.com"
LINKEDIN_URN = "ACoAAEW7rMoB7lBmW3WjmftG4hJral0NnTAfK9E"  # your provided URN
GITHUB_USERNAME = "Venkateswararaobhimasingi"         # your github username

from django.utils.dateparse import parse_datetime

def _save_activity(platform, native_id, title, message, url=None, meta=None, published=None):
    activity_id = f"{platform}:{native_id}"
    if FeedActivity.objects.filter(activity_id=activity_id).exists():
        return False

    published_at = None
    if published:
        if isinstance(published, str):
            published_at = parse_datetime(published)
        elif isinstance(published, (int, float)):
            # timestamp seconds → datetime
            published_at = timezone.datetime.fromtimestamp(published, tz=timezone.utc)

    FeedActivity.objects.create(
        platform=platform,
        activity_id=activity_id,
        title=title or (message[:120] if message else native_id),
        message=message or "",
        url=url,
        meta=meta or {},
        published_at=published_at,
    )
    return True


# ---------- LinkedIn ----------
def fetch_linkedin_posts(rapidapi_key: str | None = None, page: int = 1):
    """Fetch LinkedIn posts via RapidAPI endpoint and save new ones.

    Returns: dict with counts: {'fetched': n, 'saved': m, 'error': None or str}
    """
    if rapidapi_key is None:
        rapidapi_key = os.getenv("LINKEDIN_RAPIDAPI_KEY")
    if not rapidapi_key:
        return {"fetched": 0, "saved": 0, "error": "Missing RapidAPI key"}

    url = f"https://{LINKEDIN_API_HOST}/api/v1/user/posts"
    params = {"urn": LINKEDIN_URN, "page": page}
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": LINKEDIN_API_HOST,
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
    except Exception as e:
        return {"fetched": 0, "saved": 0, "error": f"Request error: {e}"}

    if resp.status_code != 200:
        return {"fetched": 0, "saved": 0, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

    try:
        payload = resp.json()
    except ValueError:
        return {"fetched": 0, "saved": 0, "error": "Invalid JSON response", "raw": resp.text}

    # The RapidAPI response structure may use 'data', 'posts' etc. Be defensive:
    items = payload.get("data") or payload.get("posts") or payload.get("items") or []
    saved = 0
    fetched = len(items)

    for item in items:
        # adapt to fields present in the API
        
        native_id = item.get("urn") or item.get("id") or item.get("activityUrn") or item.get("activity_id") or str(item.get("created", "") + "_" + str(item.get("text", "")[:10]))
        text = item.get("text") or item.get("content") or item.get("description") or ""
        created_time = item.get("created_at") or item.get("time") or item.get("timestamp")
        link = item.get("url") or item.get("permalink") or None
        meta = item
        print(created_time)
        saved_flag = _save_activity("linkedin", native_id, title=(text[:120] if text else "LinkedIn post"), message=text, url=link, meta=meta,published=created_time)
        if saved_flag:
            saved += 1

    return {"fetched": fetched, "saved": saved, "error": None}

# ---------- GitHub ----------
import os
import requests
from django.conf import settings

GITHUB_TOKEN = settings.GITHUB_TOKEN # store securely in env var
GITHUB_USERNAME ="Venkateswararaobhimasingi" 

def fetch_github_events(username: str | None = None):
    """Fetch public GitHub events for username and save new ones."""
    if username is None:
        username = GITHUB_USERNAME

    url = f"https://api.github.com/users/{username}/events/public"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }

    # ✅ Add token if available
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except Exception as e:
        return {"fetched": 0, "saved": 0, "error": f"Request error: {e}"}

    if resp.status_code != 200:
        return {"fetched": 0, "saved": 0, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

    try:
        events = resp.json()
    except ValueError:
        return {"fetched": 0, "saved": 0, "error": "Invalid JSON response"}

    saved = 0
    fetched = len(events)
    for ev in events:
        native_id = ev.get("id") or str(ev.get("created_at", "") + "_" + ev.get("type", ""))
        ev_type = ev.get("type", "Event")
        repo_name = ev.get("repo", {}).get("name", "")
        created_at = ev.get("created_at")

        # Build a friendly title and message
        title = f"{ev_type} on {repo_name}" if repo_name else ev_type
        message = ev.get("type", "")

        html_url = None
        if ev_type == "PushEvent":
            html_url = f"https://github.com/{repo_name}"
            commits = ev.get("payload", {}).get("commits", [])
            cm = "\n".join([f"- {c.get('message','(no message)')}" for c in commits])
            message = f"Push to {repo_name}\n{cm}" if commits else f"Push to {repo_name}"
        elif ev_type == "CreateEvent":
            ref_type = ev.get("payload", {}).get("ref_type")
            message = f"Created {ref_type} on {repo_name}"
            html_url = f"https://github.com/{repo_name}"

        # ✅ Save activity (assuming _save_activity is your function)
        saved_flag = _save_activity(
            "github",
            native_id,
            title=title,
            message=message,
            url=html_url,
            meta=ev,
            published=created_at
        )
        if saved_flag:
            saved += 1

    return {"fetched": fetched, "saved": saved, "error": None}
