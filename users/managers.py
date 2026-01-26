"""
User model manager.

Defines a single entry point for creating User instances.
Managers centralize creation logic and enforce core invariants (identity,
security, and role consistency) across all user creation paths.
"""

from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager

if TYPE_CHECKING:
    from .models import User


class UserManager(BaseUserManager):
    """
    Custom manager for the User model that:
      - normalizes email
      - hashes passwords via set_password()
      - provides create_user and create_superuser helpers consumed by Django management commands
    """

    use_in_migrations = True

    def _create_user(self, email: str, password: str, **extra_fields: Any) -> "User":
        """
        Internal helper that performs the actual User creation.

        Orchestrates logic for email normalization, password hashing,
        and persistence.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, **extra_fields)

        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str, **extra_fields: Any) -> "User":
        """
        Creates a standard (non-staff, non-admin) user.

        Applies safe default flags for regular accounts and delegates
        creation self._create_user().
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields: Any) -> "User":
        """
        Creates an administrative user with extended permissions.

        Enforces required 'staff' and 'superuser' flags to prevent
        misconfigured admin accounts.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)
