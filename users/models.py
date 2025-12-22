from typing import ClassVar

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Canonical user model for an e-commerce app:
      - email is the primary identifier (unique)
      - is_email_verified is separate from is_active
      - keep schema minimal: extend via related models (CustomerProfile, AuthProvider)
    """

    email = models.EmailField("email address", unique=True, db_index=True)
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this user should be treated as active. "
        "Unselect instead of deleting accounts.",
    )
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can access the admin site.",
    )
    is_email_verified = models.BooleanField(
        "email verified",
        default=False,
        help_text="Designates whether the user's email has been verified.",
    )

    date_joined = models.DateTimeField("date joined", default=timezone.now)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    objects = UserManager()

    USERNAME_FIELD: ClassVar[str] = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []  # email is required and the username field

    class Meta:
        ordering = ("-date_joined",)
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self) -> str:
        return self.email

    @property
    def is_verified(self) -> bool:
        """Ensures that is_verified is read-only."""
        return self.is_email_verified


class AuthProvider(models.Model):
    """
    Links external auth providers (Google, GitHub, Apple, etc.) to a User.
    This makes it straightforward to:
      - attach multiple providers to one user
      - store provider-specific flags (e.g. email_verified_by_provider)
      - revoke provider links independently
    """

    PROVIDER_CHOICES = (
        ("local", "Local"),
        ("google", "Google"),
        ("github", "GitHub"),
        ("apple", "Apple"),
        ("facebook", "Facebook"),
    )

    user = models.ForeignKey(User, related_name="auth_providers", on_delete=models.CASCADE)
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    provider_uid = models.CharField(
        max_length=255, help_text="Unique id returned by provider", db_index=True
    )
    email = models.EmailField(help_text="Email returned by provider", blank=True, null=True)
    email_verified_by_provider = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("provider", "provider_uid")
        indexes = [
            models.Index(fields=["provider", "provider_uid"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.provider_uid} -> {self.user.email}"
