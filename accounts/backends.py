from django.contrib.auth.backends import ModelBackend


class VerifiedModelBackend(ModelBackend):
    """Refuses authentication (site, /admin/ and API basic-auth) until the email is verified."""

    def user_can_authenticate(self, user):
        return super().user_can_authenticate(user) and getattr(user, "email_verified", True)