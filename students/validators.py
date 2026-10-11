import os

from django.core.exceptions import ValidationError

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
RESUME_EXT = {".pdf", ".doc", ".docx"}


def _check(file, allowed, max_mb):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed:
        raise ValidationError(f"Unsupported file type. Allowed: {', '.join(sorted(allowed))}")
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(f"File is too large. Maximum size is {max_mb} MB.")


def validate_image(file):
    _check(file, IMAGE_EXT, 2)


def validate_resume(file):
    _check(file, RESUME_EXT, 5)
