from typing import Any, Mapping

from django.core.exceptions import ValidationError as DjangoValidationError
from jsonschema import Draft7Validator, SchemaError


class SchemaValidator:
    """This will be a class for schema validation."""

    @staticmethod
    def get_validator_for_schema(schema: Mapping[str, Any]) -> Draft7Validator:
        return Draft7Validator(schema)

    @staticmethod
    def validate_schema(schema: Mapping[str, Any]) -> None:
        """
        Validate the JSON schema for correctness + enforce ProductType rules.
        """
        try:
            Draft7Validator.check_schema(schema)
        except SchemaError as e:
            raise DjangoValidationError({"attributes_schema": str(e)}) from e

        schema_type = schema.get("type")
        if schema_type and schema_type != "object":
            raise DjangoValidationError({"attributes_schema": "Top-level type must be 'object'."})

    @staticmethod
    def validate_attributes(schema: Mapping[str, Any], attributes: Mapping[str, Any]) -> None:
        """
        Validate an attributes instance against a schema.
        """
        SchemaValidator.validate_schema(schema)

        validator = SchemaValidator.get_validator_for_schema(schema)
        validator.validate(instance=attributes)
