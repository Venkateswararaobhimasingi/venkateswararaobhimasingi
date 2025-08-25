from django.shortcuts import render

# Create your views here.
import requests
from django.shortcuts import render

import os
from django.conf import settings
import requests
from django.shortcuts import render

import requests
from django.conf import settings
from .models import Repository

import requests
from django.conf import settings
from .models import Repository

from django.http import JsonResponse
import requests
from django.conf import settings
from .models import Repository, GitHubToken

def sync_github_repos(request):
    token1 = GitHubToken.objects.filter(name='github').first()
    token=token1.token
    url = "https://api.github.com/user/repos?per_page=100&sort=created&direction=desc"
    headers = {"Authorization": f"token {token}"}

    response = requests.get(url, headers=headers)
    repos = response.json()
    #print(repos)

    saved_count = 0
    owner = "Venkateswararaobhimasingi"

    for repo in repos:
        if repo.get("fork", False):
            continue  # skip forks

        name = repo["name"]

        # Check for image.png in repo
        raw_image_url = f"https://raw.githubusercontent.com/{owner}/{name}/main/image.png"
        try:
            check = requests.head(raw_image_url)
            if check.status_code == 200:
                image_url = raw_image_url
            else:
                image_url = f"https://i.imgur.com/llHed9n.jpeg"
        except Exception:
            image_url = f"https://i.imgur.com/llHed9n.jpeg"

        # Fallback to default.png if still empty
        if not image_url:
            image_url = "https://i.imgur.com/llHed9n.jpeg"

        Repository.objects.update_or_create(
            name=name,
            defaults={
                "url": repo["html_url"],
                "description": repo.get("description", "No description provided."),
                "private": repo["private"],
                "image": image_url,
            },
        )
        saved_count += 1

    return JsonResponse({"fetched": len(repos), "saved": saved_count})



from django.shortcuts import render
from .models import Repository

def github_projects(request):
    exclude_list = [
        "test1", "git-base", "search-and-filter", "base",
        "141164246", "workoutlog", "week1", "paymentwebsite",
        "week2", "DAP"
    ]
    exclude_urls = [
        "https://github.com/me50/Venkateswararaobhimasingi"
    ]

    projects = Repository.objects.exclude(name__in=exclude_list).exclude(url__in=exclude_urls)

    return render(request, "core/github.html", {"projects": projects})






from django.conf import settings
from django.shortcuts import render
import requests

def home(request):
    # GitHub API call
   

    return render(
        request,
        "core/profile.html",
        {
            "img_url": "/static/my_img.jpg",
            "project_count": 25,
        },
    )


def profile(request):
    return render(request,'core/profile.html')


def base(request):
    return render(request,'core/base.html')

import http.client
import json
from django.shortcuts import render
from django.http import JsonResponse

def linkedin_posts(request):
    conn = http.client.HTTPSConnection("fresh-linkedin-scraper-api.p.rapidapi.com")

    headers = {
        "x-rapidapi-key": "159cfbdd1fmsh8906124a5ce0f7dp1665c4jsnfd7eeadf70ac",
        "x-rapidapi-host": "fresh-linkedin-scraper-api.p.rapidapi.com",
    }

    # FIXED URL (removed &quot)
    url = "/api/v1/user/posts?urn=ACoAAEW7rMoB7lBmW3WjmftG4hJral0NnTAfK9E&page=1"

    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    if res.status != 200:
        posts = {"error": f"API returned status {res.status}", "raw": data}
    else:
        try:
            posts = json.loads(data)
        except json.JSONDecodeError:
            posts = {"error": "Could not parse JSON", "raw": data}

    # Pass data to template
    return render(request, "core/linkedin_posts.html", {"posts": posts})



import http.client
import json
from django.http import JsonResponse

def get_linkedin_urn(request, username="venkateswara-rao-bhimasingi-376981287"):
    conn = http.client.HTTPSConnection("fresh-linkedin-scraper-api.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "159cfbdd1fmsh8906124a5ce0f7dp1665c4jsnfd7eeadf70ac",
        'x-rapidapi-host': "fresh-linkedin-scraper-api.p.rapidapi.com"
    }

    # Call profile endpoint with LinkedIn vanity username
    url = f"/api/v1/user/profile?username={username}"
    conn.request("GET", url, headers=headers)

    res = conn.getresponse()
    data = res.read().decode("utf-8")

    try:
        profile = json.loads(data)
        urn = profile.get("urn")  # Extract URN from response
        name = profile.get("name")
        return JsonResponse({"status": "success", "name": name, "urn": urn, "raw": profile})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e), "raw": data})


from django.shortcuts import render
from django.http import JsonResponse
from .models import FeedActivity
from .utils import fetch_linkedin_posts, fetch_github_events
import os

def feed_view(request):
    # Sort activities by most recent of published_at or created_at
    activities = FeedActivity.objects.all().order_by(
        '-published_at', '-created_at'
    )

    return render(request, "core/feed.html", {"activities": activities})


def api_sync_feed(request):
    """HTTP endpoint to trigger immediate sync. Protect this endpoint as needed."""
    # OPTIONAL: restrict by API key or staff-only
    rapidapi_key = "159cfbdd1fmsh8906124a5ce0f7dp1665c4jsnfd7eeadf70ac"
    linkedin_result = fetch_linkedin_posts(rapidapi_key=rapidapi_key, page=1)
    github_result = fetch_github_events()
    return JsonResponse({"linkedin": linkedin_result, "github": github_result})


def resume_view(request):
    return render(request, 'core/resume.html', {
        'resume_pdf_url': '/static/VENKATESWARA_RAO_BHIMASINGI_RESUME.pdf'
    })

def skills(request):
    return render(request, 'core/skills.html', {
        'resume_pdf_url': '/static/VENKATESWARA_RAO_BHIMASINGI_RESUME.pdf'
    })

def contact(request):
    return render(request, 'core/contact.html')

from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def send_email(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        subject = f"New Contact Form Submission from {name}"
        body = f"From: {name} <{email}>\n\nMessage:\n{message}"

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,        # from (your Gmail)
            [settings.DEFAULT_TO_EMAIL],        # to (your inbox)
            fail_silently=False,
        )

        return JsonResponse({"success": True, "message": "Email sent!"})

    return JsonResponse({"success": False, "message": "Invalid request"})



import os
from django.conf import settings
from django.shortcuts import render
from datetime import datetime

def certificate(request):
    cert_dir = os.path.join(settings.MEDIA_ROOT, "certificates")
    certs = []

    if os.path.exists(cert_dir):
        for f in os.listdir(cert_dir):
            if f.endswith(".pdf"):
                date = None
                name = f.replace(".pdf", "")

                # Split name and date by "__"
                if "__" in name:
                    try:
                        name, date_str = name.rsplit("__", 1)
                        date = datetime.strptime(date_str, "%d-%m-%Y")
                    except:
                        pass

                certs.append({
                    # Replace "-" with spaces for display
                    "name": name.replace("-", " ").title(),
                    "date": date,
                    # Use MEDIA_URL path for correct serving
                    "file": f"{settings.MEDIA_URL}certificates/{f}",
                })

    # Sort by date (newest first, undated last)
    certs = sorted(certs, key=lambda x: (x["date"] is None, x["date"]), reverse=True)

    return render(request, "core/certificates.html", {"certs": certs})
