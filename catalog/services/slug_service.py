import uuid
from dataclasses import dataclass

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
