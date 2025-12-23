from typing import Any


class CleanValidationSerializerMixin:
    """
    Runs model.full_clean() during DRF serializer validation.

    Use when validation logic lives inside model.clean()
    and should be shared by Admin + DRF.
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        obj = self.instance or self.Meta.model()

        for key, value in attrs.items():
            setattr(obj, key, value)

        obj.clean()
        return attrs

class ModelDefaultsSerializerMixin:
    """
    Ensures DRF does NOT override model defaults.
    Missing fields are not sent to .create(), allowing model defaults to apply.
    """

    def to_internal_value(self, data):
        internal = super().to_internal_value(data)

        # remove fields not supplied → allow model.default to apply
        for field in list(self.fields.keys()):
            if field not in data:
                internal.pop(field, None)

        return internal

class BaseSerializerMixin(CleanValidationSerializerMixin, ModelDefaultsSerializerMixin):
    ...
