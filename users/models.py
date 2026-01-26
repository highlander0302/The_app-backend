"""
User and authentication models.

Contains the main User model and related models for authentication.
The User model holds core account data, while external login methods
are stored separately in AuthProvider.
"""

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
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    class Meta:
        ordering = ("-date_joined",)
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self) -> str:
        return self.email


class ProviderChoices(models.TextChoices):
    """
    Defines the allowed external authentication providers.

    Using TextChoices centralizes provider values, prevents typos.
    """

    LOCAL = "local", "Local"
    GOOGLE = "google", "Google"
    GITHUB = "github", "GitHub"
    FACEBOOK = "facebook", "Facebook"


class AuthProvider(models.Model):
    """
    Links a User to external authentication providers.

    Separating providers from User allows one account to have multiple
    login methods and keeps provider-specific data out of the core user model.
    """

    user = models.ForeignKey(
        "User",
        related_name="auth_providers",
        on_delete=models.CASCADE,
    )
    provider = models.CharField(
        max_length=50,
        choices=ProviderChoices.choices,
    )
    provider_uid = models.CharField(
        max_length=1024,
        db_index=True,
    )
    email = models.EmailField(blank=True, null=True)
    email_verified_by_provider = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Ensures each external provider account can be linked to only one user.
        Prevents duplicate or conflicting identity links.
        """

        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_uid"],
                name="uniq_provider_uid",
            )
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.provider_uid} -> {self.user.email}"
