from django.contrib import admin

from .models import Skill, StudentSkill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ("student", "skill", "level", "years")
    list_filter = ("level",)
    autocomplete_fields = ("skill",)
