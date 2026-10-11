from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Organization(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organization")
    name = models.CharField(max_length=150, unique=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Opportunity(models.Model):
    class Type(models.TextChoices):
        INTERNSHIP = "internship", "Internship"
        JOB = "job", "Job"
        HACKATHON = "hackathon", "Hackathon"
        SCHOLARSHIP = "scholarship", "Scholarship"
        WORKSHOP = "workshop", "Workshop"
        CERTIFICATION = "certification", "Certification"
        EVENT = "event", "Event"
        FREELANCE = "freelance", "Freelance"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="opportunities")
    title = models.CharField(max_length=150)
    opportunity_type = models.CharField(max_length=15, choices=Type.choices, db_index=True)
    description = models.TextField()
    location = models.CharField(max_length=100, blank=True, db_index=True)
    is_remote = models.BooleanField(default=False)
    compensation = models.CharField("stipend / salary", max_length=80, blank=True)
    deadline = models.DateField(null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField("skills.Skill", through="OpportunitySkill", related_name="opportunities")

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "opportunities"
        indexes = [models.Index(fields=["is_active", "deadline"])]

    def __str__(self):
        return f"{self.title} @ {self.organization}"

    @property
    def is_expired(self):
        return bool(self.deadline and self.deadline < timezone.localdate())

    @property
    def is_open(self):
        return self.is_active and not self.is_expired

    @property
    def days_left(self):
        return (self.deadline - timezone.localdate()).days if self.deadline else None


class OpportunitySkill(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    skill = models.ForeignKey("skills.Skill", on_delete=models.PROTECT)
    weight = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["opportunity", "skill"], name="uniq_opportunity_skill")]
        ordering = ["-weight", "skill__name"]

    def __str__(self):
        return f"{self.skill} (w{self.weight})"


class SavedOpportunity(models.Model):
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="saved")
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "opportunity"], name="uniq_saved_opportunity")]
        ordering = ["-saved_at"]
