from django.contrib import admin

from .models import Certification, Education, Project, StudentProfile


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "location", "career_goal")
    search_fields = ("full_name", "user__username", "location")
    inlines = [EducationInline, ProjectInline]


admin.site.register(Certification)
