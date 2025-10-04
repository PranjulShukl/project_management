from django.db import models
from django.conf import settings
from django.utils import timezone

class Project(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    
    name = models.CharField("Name of the Project", max_length=255)
    category = models.CharField(  # Changed: removed choices
        "Category of the Project",
        max_length=100,   # you can adjust size
    )
    tender_award_date = models.DateField("Date on which Tender awarded")
    completion_date = models.DateField("Date of tentative Completion")
    company = models.CharField("Company name allocating Project", max_length=255)
    location = models.CharField("Location of installation", max_length=255)
    description = models.TextField("Description of Project")
    is_submitted = models.BooleanField(default=False)
    submission_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    # updated_at removed
    client_email = models.EmailField(null=True, blank=True)
    client_feedback = models.TextField(null=True, blank=True)
    client_confirmed_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class WorkLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='work_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_logs')
    date = models.DateField()
    description = models.TextField(help_text="Describe the work done today")
    hours_worked = models.DecimalField(max_digits=4, decimal_places=1, help_text="Number of hours worked")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        # Ensure a user can only create one work log per project per day
        unique_together = ['project', 'user', 'date']

    def __str__(self):
        return f"{self.project.name} - {self.date} - {self.user.username}"



import uuid

class FeedbackToken(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def mark_used(self):
        self.used = True
        self.save()