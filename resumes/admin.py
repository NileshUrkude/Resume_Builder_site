from django.contrib import admin

from .models import (
    Achievement,
    Certificate,
    Education,
    Experience,
    Hobby,
    Language,
    Project,
    Resume,
    ResumeEvent,
    Skill,
)


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('resume_name', 'full_name', 'user', 'preferred_template', 'is_public', 'updated_at')
    list_filter = ('preferred_template', 'is_public', 'user')
    search_fields = ('full_name', 'email', 'resume_name', 'user__username')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    inlines = [EducationInline, ExperienceInline, ProjectInline, SkillInline]


@admin.register(ResumeEvent)
class ResumeEventAdmin(admin.ModelAdmin):
    list_display = ('resume', 'event_type', 'template', 'created_at')
    list_filter = ('event_type',)
