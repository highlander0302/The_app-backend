"""
Provides validation for product variant relationships.

Includes checks for:
- Circular variant chains (no product can reference itself as a variant).
- Variant integrity
    (a product cannot be its own variant and must share the same product type as its parent).

Raises DjangoValidationError for any violations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError as DjangoValidationError

if TYPE_CHECKING:
    from catalog.models import Product


class VariantValidator:
    """
    Validates the variant_of relationships of Product instances.

    Methods:
        validate_chain(product_instance):
            Ensures there are no cycles in the `variant_of` chain.
        validate_integrity(product_instance):
            Ensures a product is not its own variant
            and that variant and parent are the same product type.

    Both methods raise DjangoValidationError on validation failure.
    """

    @staticmethod
    def validate_chain(product_instance: Product) -> None:
        """
        Checks each parent in the `variant_of` chain starting from `product_instance`.
        Raises a DjangoValidationError if a circular relationship is detected.
        Uses the database PK for existing products and the Python `id()` for objects not yet saved,
        so the error message identifies the specific products forming the cycle.
        """
        parent_of_product: Product | None = product_instance.variant_of
        seen_parents = set()

        product_key = product_instance.pk or id(product_instance)
        while parent_of_product:
            parent_key = parent_of_product.pk or id(parent_of_product)

            if parent_key == product_key or parent_key in seen_parents:
                raise DjangoValidationError(
                    {
                        "variant_of": (
                            f"Circular variant relationship detected! "
                            f"Product {product_key} and parent {parent_key} form a cycle."
                        )
                    }
                )

            seen_parents.add(parent_key)
            parent_of_product = parent_of_product.variant_of

    @staticmethod
    def validate_integrity(product_instance: Product) -> None:
        """
        Checks two things:
        1. A product cannot be a variant of itself.
        2. A variant must have the same product type as its parent.
        """
        parent_of_product: Product | None = product_instance.variant_of
        if not parent_of_product:
            return

        if (
            product_instance.pk
            and parent_of_product.pk
            and product_instance.pk == parent_of_product.pk
        ):
            raise DjangoValidationError(
                {
                    "variant_of": (
                        f"A product cannot be a variant of itself. "
                        f"Product {product_instance.name} references itself as parent."
                    )
                }
            )

        parent_key = parent_of_product.pk or id(parent_of_product)
        if parent_of_product.product_type_id != product_instance.product_type_id:
            raise DjangoValidationError(
                {
                    "variant_of": (
                        f"Product {product_instance.name} can't be a variant of "
                        f"parent {parent_key}, because their product types differ "
                        f"({product_instance.product_type_id} vs "
                        f"{parent_of_product.product_type_id})."
                    )
                }
            )
