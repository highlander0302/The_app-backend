import uuid
from dataclasses import dataclass
from typing import Generator, Optional

from django.db import models
from django.utils.text import slugify


@dataclass(frozen=True)
class SlugConfig:
    max_length: int = 100
    uuid_suffix_length: int = 8

    @property
    def suffix_length(self) -> int:
        return self.uuid_suffix_length + 1


class SlugService:
    @staticmethod
    def ensure_base_slug_len(base: str, cfg: SlugConfig) -> str:
        allowed_len = cfg.max_length - cfg.suffix_length
        if len(base) > allowed_len:
            last_dash = base[:allowed_len].rfind("-")
            truncated = base[:last_dash] if last_dash != -1 else base[:allowed_len]
            truncated = truncated.strip("-")
            return truncated or "product"
        return base

    @staticmethod
    def suffix_base_slug(base: str, cfg: SlugConfig) -> str:
        uuid_suffix = uuid.uuid4().hex[: cfg.uuid_suffix_length]
        return f"{base}-{uuid_suffix}"

    @staticmethod
    def make_base(name: str) -> str:
        return slugify(name) or "product"

    @classmethod
    def generate_candidates(cls, name: str, cfg: SlugConfig) -> Generator[str, None, None]:
        """
        Yield base slug first, then unlimited suffixed candidates.
        """
        base = cls.ensure_base_slug_len(cls.make_base(name), cfg)
        yield base
        while True:
            yield cls.suffix_base_slug(base, cfg)

    @staticmethod
    def slug_exists(
        model_class: type[models.Model], slug: str, exclude_pk: Optional[int] = None
    ) -> bool:
        """
        DB-level existence check for the given model class.
        `exclude_pk` follows the same semantics as your previous method.
        """
        qs = model_class.objects.filter(slug=slug)
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        return qs.exists()

    @classmethod
    def generate_unique_slug(
        cls,
        model_class: type[models.Model],
        name: str,
        cfg: SlugConfig,
        exclude_pk: Optional[int] = None,
    ) -> str:
        """
        Return the first candidate slug that does not exist in DB for `model_class`.
        No max attempts — infinite generator is acceptable for your context.
        """
        for candidate in cls.generate_candidates(name, cfg):
            if not cls.slug_exists(model_class, candidate, exclude_pk=exclude_pk):
                return candidate
        raise RuntimeError("Failed to generate unique slug")
