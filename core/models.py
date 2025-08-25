from django.db import models

# Create your models here.
class FeedActivity(models.Model):
    PLATFORM_CHOICES = (
        ("linkedin", "LinkedIn"),
        ("github", "GitHub"),
    )

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    activity_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=400, blank=True)
    message = models.TextField(blank=True)
    url = models.URLField(blank=True, null=True)
    meta = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)  # saved in DB
    published_at = models.DateTimeField(null=True, blank=True)  # actual platform timestamp

    class Meta:
        ordering = ("-published_at", "-created_at")

from django.db import models

class Repository(models.Model):
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField()
    description = models.TextField(blank=True, null=True)
    private = models.BooleanField(default=False)
    image = models.URLField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
