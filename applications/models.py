from django.db import models


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "Applied", "Applied"
        UNDER_REVIEW = "Under Review", "Under Review"
        SHORTLISTED = "Shortlisted", "Shortlisted"
        INTERVIEW = "Interview", "Interview"
        SELECTED = "Selected", "Selected"
        REJECTED = "Rejected", "Rejected"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="applications")
    opportunity = models.ForeignKey("opportunities.Opportunity", on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.APPLIED, db_index=True)
    cover_letter = models.TextField(blank=True, max_length=2000)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [models.UniqueConstraint(fields=["student", "opportunity"], name="uniq_student_opportunity_application")]

    def __str__(self):
        return f"{self.student} -> {self.opportunity} [{self.status}]"
