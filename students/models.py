from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from .validators import validate_image, validate_resume

phone_validator = RegexValidator(r"^\+?[0-9 \-]{7,15}$", "Enter a valid phone number.")


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True, validators=[phone_validator])
    location = models.CharField(max_length=100, blank=True, db_index=True)
    bio = models.TextField(blank=True, max_length=1000)
    career_goal = models.CharField(max_length=150, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="profiles/", blank=True, validators=[validate_image])
    resume = models.FileField(upload_to="resumes/", blank=True, validators=[validate_resume])
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.user.username

    @property
    def completeness(self):
        checks = [self.full_name, self.phone, self.location, self.bio, self.career_goal, self.resume,
                  self.student_skills.exists(), self.educations.exists(), self.projects.exists()]
        return int(sum(bool(c) for c in checks) / len(checks) * 100)


class Education(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="educations")
    degree = models.CharField(max_length=120)
    institution = models.CharField(max_length=150)
    field_of_study = models.CharField(max_length=120, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    grade = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["-end_date", "-start_date"]

    def __str__(self):
        return f"{self.degree}, {self.institution}"


class Project(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    technologies = models.CharField(max_length=200, blank=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)

    def __str__(self):
        return self.title


class Certification(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=150)
    issuer = models.CharField(max_length=120)
    issued_on = models.DateField(null=True, blank=True)
    credential_url = models.URLField(blank=True)

    def __str__(self):
        return self.name
