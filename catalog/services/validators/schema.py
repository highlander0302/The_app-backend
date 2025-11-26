"""
Module for validating JSON schemas and attribute instances.

Provides SchemaValidator with methods to:
- Check that a schema is valid and conforms to ProductType rules.
- Validate attribute data against a schema.

Uses jsonschema.Draft7Validator for validation and raises
ValidationError on failure.
"""

from typing import Any, Mapping

from django.core.exceptions import ValidationError
from jsonschema import Draft7Validator, SchemaError
from jsonschema import ValidationError as JSONSchemaValidationError


class SchemaValidator:
    """Validates JSON schemas and attribute instances."""

    @staticmethod
    def validate_schema(schema: Mapping[str, Any]) -> None:
        """Ensure the schema is valid and top-level type is 'object'."""
        try:
            Draft7Validator.check_schema(schema)
        except SchemaError as e:
            raise ValidationError({"attributes_schema": str(e)}) from e

        schema_type = schema.get("type")
        if schema_type and schema_type != "object":
            raise ValidationError({"attributes_schema": "Top-level type must be 'object'."})

    @classmethod
    def validate_attributes(cls, schema: Mapping[str, Any], attributes: Mapping[str, Any]) -> None:
        """Validate a data instance against the given schema."""
        cls.validate_schema(schema)

        validator = Draft7Validator(schema)
        try:
            validator.validate(instance=attributes)
        except JSONSchemaValidationError as e:
            raise ValidationError({"attributes": str(e)}) from e
