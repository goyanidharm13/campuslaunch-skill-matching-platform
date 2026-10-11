from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)
    category = models.CharField(max_length=60, db_index=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        super().save(*args, **kwargs)


class StudentSkill(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "Beginner", "Beginner"
        INTERMEDIATE = "Intermediate", "Intermediate"
        ADVANCED = "Advanced", "Advanced"
        EXPERT = "Expert", "Expert"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="student_skills")
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name="student_skills")
    level = models.CharField(max_length=15, choices=Level.choices, default=Level.BEGINNER)
    years = models.DecimalField(max_digits=3, decimal_places=1, default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "skill"], name="uniq_student_skill")]
        ordering = ["skill__name"]

    def __str__(self):
        return f"{self.student} - {self.skill} ({self.level})"
