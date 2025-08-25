from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import FeedActivity,Repository
@admin.register(FeedActivity)
class FeedActivityAdmin(admin.ModelAdmin):
    list_display = ("platform", "title", "activity_id", "created_at")
    search_fields = ("platform", "title", "activity_id")
    readonly_fields = ("meta", "created_at")

from django.contrib import admin
from .models import Repository   # import the model

admin.site.register(Repository)