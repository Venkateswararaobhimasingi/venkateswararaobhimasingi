from django.urls import path
from . import views

urlpatterns = [
    path("github/", views.github_projects, name="github"),
    path('',views.home,name='home'),
    path("linkedin/", views.linkedin_posts, name="linkedin_posts"),
    path("feed/", views.feed_view, name="feed"),
    path("sync_feed/", views.api_sync_feed, name="api_sync_feed"),
    path('profile',views.profile,name='profile'),
    path('base',views.base,name='base'),
    path('resume/', views.resume_view, name='resume'),
    path('skills/', views.skills, name='skills'),
    path('contact/', views.contact, name='contact'),
    path('send/', views.send_email, name='send_email'),
    path("certificate/", views.certificate, name="certificate"),
    path('sync_github_repos/', views.sync_github_repos, name='sync_github_repos'),
]
