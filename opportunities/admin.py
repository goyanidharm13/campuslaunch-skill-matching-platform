from django.contrib import admin

from .models import Opportunity, OpportunitySkill, Organization, SavedOpportunity


class OpportunitySkillInline(admin.TabularInline):
    model = OpportunitySkill
    extra = 1
    autocomplete_fields = ("skill",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "location")
    search_fields = ("name",)


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "opportunity_type", "location", "deadline", "is_active")
    list_filter = ("opportunity_type", "is_active", "is_remote")
    search_fields = ("title", "organization__name")
    inlines = [OpportunitySkillInline]


admin.site.register(SavedOpportunity)
