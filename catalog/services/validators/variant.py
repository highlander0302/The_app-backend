from django.core.exceptions import ValidationError as DjangoValidationError

from catalog.models import Product


class VariantValidator:
    @staticmethod
    def validate_chain(product_instance: "Product") -> None:
        parent = product_instance.variant_of
        seen = set()

        while parent:
            parent_key = parent.pk or id(parent)
            product_key = product_instance.pk or id(product_instance)

            if parent_key == product_key or parent_key in seen:
                raise DjangoValidationError(
                    {"variant_of": "Circular variant relationship detected."}
                )

            seen.add(parent_key)
            parent = parent.variant_of

    @staticmethod
    def validate_integrity(product_instance: "Product") -> None:
        parent = product_instance.variant_of
        if not parent:
            return

        if product_instance.pk and parent.pk and product_instance.pk == parent.pk:
            raise DjangoValidationError({"variant_of": "A product cannot be a variant of itself."})

        if parent.product_type_id != product_instance.product_type_id:
            raise DjangoValidationError(
                {"variant_of": "A variant must have the same product type as its parent."}
            )
