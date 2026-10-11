from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from opportunities.models import Organization
from students.models import StudentProfile

from .models import User


class OrganizationInline(admin.StackedInline):
    model = Organization
    extra = 0
    max_num = 1
    fields = ("name", "website", "location", "description")


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    extra = 0
    max_num = 1
    fields = ("full_name", "phone", "location", "career_goal")


@admin.register(User)
class CampusUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active")
    search_fields = ("username", "email")
    actions = ["deactivate_users", "activate_users"]
    fieldsets = UserAdmin.fieldsets + (("CampusLaunch", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("CampusLaunch", {"fields": ("email", "role")}),)

    def get_inline_instances(self, request, obj=None):
        """Show the organization form for recruiters and the profile form for students."""
        if obj is None:
            return []
        inlines = {User.Role.RECRUITER: [OrganizationInline],
                   User.Role.STUDENT: [StudentProfileInline]}.get(obj.role, [])
        return [inline(self.model, self.admin_site) for inline in inlines]

    @admin.action(description="Deactivate selected users (keeps their data)")
    def deactivate_users(self, request, queryset):
        updated = queryset.exclude(pk=request.user.pk).update(is_active=False)
        self.message_user(request, f"{updated} user(s) deactivated.")

    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        self.message_user(request, f"{queryset.update(is_active=True)} user(s) activated.")

admin.site.site_header = "CampusLaunch Admin"
admin.site.site_title = "CampusLaunch Admin"
admin.site.index_title = "Manage users, skills, organizations and opportunities"        