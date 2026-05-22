import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

TEMPLATE_CHOICES = [
    ('t1', 'Classic'),
    ('t2', 'Modern'),
    ('t3', 'Minimal'),
    ('t4', 'Sidebar'),
    ('t5', 'Timeline'),
    ('t6', 'Compact'),
    ('t7', 'Academic'),
    ('t8', 'Creative'),
]

FONT_CHOICES = [
    ('Arial', 'Arial'),
    ('Georgia', 'Georgia'),
    ('Inter', 'Inter'),
    ('Times New Roman', 'Times New Roman'),
]

SKILL_LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('expert', 'Expert'),
]

LANGUAGE_LEVEL_CHOICES = [
    ('basic', 'Basic'),
    ('conversational', 'Conversational'),
    ('fluent', 'Fluent'),
    ('native', 'Native'),
]


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    resume_name = models.CharField(max_length=100, default='My Resume')
    is_public = models.BooleanField(default=False)
    share_password = models.CharField(max_length=128, blank=True)
    share_expires_at = models.DateTimeField(blank=True, null=True)

    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    preferred_template = models.CharField(max_length=3, choices=TEMPLATE_CHOICES, default='t1')
    accent_color = models.CharField(max_length=7, default='#4f46e5')
    font_family = models.CharField(max_length=50, choices=FONT_CHOICES, default='Arial')

    title = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    summary = models.TextField(blank=True)
    github = models.URLField(blank=True, default='')
    linkedin = models.URLField(blank=True, default='')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.resume_name} ({self.full_name})'

    def is_share_valid(self):
        if not self.is_public:
            return False
        if self.share_expires_at and self.share_expires_at < timezone.now():
            return False
        return True

    def duration_display(self, start, end):
        if start and end:
            return f'{start.strftime("%b %Y")} – {end.strftime("%b %Y")}'
        if start:
            return f'{start.strftime("%b %Y")} – Present'
        return ''


class OrderedSectionMixin(models.Model):
    order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['order', 'id']


class Education(OrderedSectionMixin, models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=100)
    college = models.CharField(max_length=150)
    location = models.CharField(max_length=100, blank=True, default='')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True)

    def date_range(self):
        return self.resume.duration_display(self.start_date, self.end_date) or self.duration


class Experience(OrderedSectionMixin, models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def date_range(self):
        return self.resume.duration_display(self.start_date, self.end_date) or self.duration

    def bullet_points(self):
        lines = []
        for line in self.description.splitlines():
            line = line.strip().lstrip('•-*').strip()
            if line:
                lines.append(line)
        return lines


class Project(OrderedSectionMixin, models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    tech_stack = models.CharField(max_length=200, blank=True)

    def bullet_points(self):
        lines = []
        for line in self.description.splitlines():
            line = line.strip().lstrip('•-*').strip()
            if line:
                lines.append(line)
        return lines


class Skill(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default='intermediate')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']


class Certificate(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='certificates')
    name = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']


class Achievement(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']


class Language(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=80)
    proficiency = models.CharField(max_length=20, choices=LANGUAGE_LEVEL_CHOICES, default='fluent')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']


class Hobby(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='hobbies')
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']


class ResumeEvent(models.Model):
    EVENT_TYPES = [
        ('view', 'Template view'),
        ('pdf', 'PDF download'),
        ('docx', 'DOCX download'),
        ('share', 'Public share view'),
    ]
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    template = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
