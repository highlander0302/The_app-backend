"""
Slug generation service for products.

This module provides a configurable service to generate unique, URL-friendly
slugs for products.

It handles:
- Creating a base slug from a string (e.g., product name) using `slugify`.
- Ensuring the base slug fits within a maximum length.
- Generating unique suffixed slugs using a UUID when needed.
- Checking the database to avoid collisions with existing slugs.

Classes:
    SlugConfig: Configuration for slug generation (max length, UUID suffix length).
    SlugService: Service for generating and validating unique slugs.
"""

import uuid
from dataclasses import dataclass
from typing import Generator

from django.db import models
from django.utils.text import slugify


@dataclass(frozen=True)
class SlugConfig:
    """Configuration for slug generation."""

    max_length: int = 100
    uuid_suffix_length: int = 8

    @property
    def suffix_length(self) -> int:
        """Total length added by the suffix, including the dash."""
        return self.uuid_suffix_length + 1


class SlugService:
    """
    Service for generating unique, URL-friendly slugs for products.

    This service handles:
    - Creating a base slug from a string (product name).
    - Truncating the base slug to fit max length.
    - Generating suffixed slugs with UUID to ensure uniqueness.
    - Checking the database to avoid collisions with existing slugs.

    Attributes:
        _config (SlugConfig): Configuration for slug generation, including max length
            and UUID suffix length.

    Methods:
        generate_unique_slug(model_class, name, exclude_pk):
            Returns a unique slug for the given model class.
        slug_exists(model_class, slug, exclude_pk):
            Checks if a slug already exists in the database, excluding a given PK
                (if object already exists).
    """

    def __init__(self, config: SlugConfig) -> None:
        self._config = config

    def generate_unique_slug(
        self,
        model_class: type[models.Model],
        name: str,
        exclude_pk: int | None = None,
    ) -> str:
        """
        Return the first candidate slug that does not exist in DB for `model_class`.
        """
        for candidate in self._generate_candidate_slugs(name):
            if not self.slug_exists(model_class, candidate, exclude_pk=exclude_pk):
                return candidate
        raise RuntimeError("Failed to generate unique slug")

    @staticmethod
    def slug_exists(
        model_class: type[models.Model], slug: str, exclude_pk: int | None = None
    ) -> bool:
        """
        DB-level existence check for the given model class.
        `exclude_pk` excludes current instance id from queryset, otherwise will find own slug in DB.
        """
        queryset = model_class.objects.filter(slug=slug)
        if exclude_pk is not None:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset.exists()

    def _generate_candidate_slugs(self, name: str) -> Generator[str, None, None]:
        """
        Yield base slug first, then unlimited suffixed candidates.
        """
        base = self._ensure_base_slug_len(self._make_base(name))
        yield base
        while True:
            yield self._suffix_base_slug(base)

    def _ensure_base_slug_len(self, base: str) -> str:
        """
        Cuts at the last '-' within the limit, strips leading/trailing dashes,
        and defaults to 'product' if empty after truncation.
        """
        allowed_len = self._config.max_length - self._config.suffix_length
        if len(base) > allowed_len:
            last_dash_in_allowed_len = base[:allowed_len].rfind("-")
            truncated = (
                base[:last_dash_in_allowed_len]
                if last_dash_in_allowed_len != -1
                else base[:allowed_len]
            ).strip("-")
            return truncated or "product"
        return base

    def _suffix_base_slug(self, base: str) -> str:
        uuid_suffix = uuid.uuid4().hex[: self._config.uuid_suffix_length]
        return f"{base}-{uuid_suffix}"

    def _make_base(self, name: str) -> str:
        return slugify(name) or "product"
