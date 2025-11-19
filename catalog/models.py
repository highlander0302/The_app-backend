import time
from typing import Any

from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from jsonschema import ValidationError as JSONSchemaValidationError
from jsonschema import validate, Draft7Validator, SchemaError


class ProductType(models.Model):
    """
    Represents a type of product with a dynamic schema.

    Fields:
    - name: e.g., "Laptop", "Smartphone"
    - category: Top-level category of the product type (e.g. laptop)
    - subcategory: Optional subcategory (e.g. gaming laptop)
    - fields: JSON dictionary defining the dynamic attributes and their types
    """

    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(
        max_length=100, help_text="Top-level category of the product type"
    )
    subcategory_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional subcategory",
    )
    fields = models.JSONField(
        default=dict,
        help_text="JSON schema of attributes, e.g., {'cpu': 'str', 'ram': 'int'}",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def _validate_schema(self) -> None:
        """
        Validates that `fields` conform to Draft 7 JSON schema type.
        """
        try:
            Draft7Validator.check_schema(self.fields)
        except SchemaError as e:
            raise DjangoValidationError({"fields": f"Invalid JSON Schema: {e.message}"})

    def save(self, *args, **kwargs):
        self._validate_schema()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """
    Concrete model. Represents a product in the marketplace.

    Each product belongs to a ProductType, which defines a JSON schema for
    dynamic attributes stored in `attributes`. These attributes are validated
    against the ProductType schema before saving.

    Fields include:
    - Identification: id, slug, name, SKU, UPC
    - Descriptions: brand, vendor, category, subcategory, description, short_description, tags
    - Pricing & Stock: cost_price, retail_price, sale_price, currency, stock_quantity,
    stock_threshold, is_in_stock
    - Physical Attributes: weight, dimensions, origin_country, shipping_required, color,
    product_size, material, variant_of
    - Media: image_main, images
    - Ratings: rating_average, review_count
    - Status: is_active, is_featured, approval_status, created_at, updated_at, deleted_at

    Key behaviors:
    - Auto-generates unique slug if missing or duplicate
    - Validates dynamic attributes against ProductType schema
    - Syncs category and subcategory from ProductType to increase category query speed
    """

    id = models.BigAutoField(primary_key=True)
    slug = models.SlugField(unique=True, blank=True, max_length=100)
    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=100, help_text="Top-level category of the product type"
    )
    subcategory = models.CharField(
        max_length=100, blank=True, help_text="Optional subcategory"
    )
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    brand = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)
    sku = models.CharField(
        max_length=100, unique=True, verbose_name="Stock Keeping Unit"
    )
    upc = models.CharField(
        max_length=100, blank=True, verbose_name="Universal Product Code"
    )

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    retail_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3, default="USD")
    stock_quantity = models.IntegerField(default=0, validators=MinValueValidator(0))
    stock_threshold = models.IntegerField(default=5, validators=MinValueValidator(0))

    weight = models.FloatField(help_text="Weight in grams (g)", null=True, blank=True)
    length = models.FloatField(
        help_text="Length in centimeters (cm)", null=True, blank=True
    )
    width = models.FloatField(
        help_text="Width in centimeters (cm)", null=True, blank=True
    )
    height = models.FloatField(
        help_text="Height in centimeters (cm)", null=True, blank=True
    )
    origin_country = models.CharField(max_length=54, blank=True)
    shipping_required = models.BooleanField(default=True)
    color = models.CharField(max_length=50, blank=True)
    product_size = models.CharField(
        max_length=50, blank=True, verbose_name="screen size in inches / resolution"
    )
    material = models.CharField(max_length=50, blank=True)
    variant_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="variants",
    )

    image_main = models.URLField(blank=True)
    images = models.JSONField(default=list, blank=True)

    rating_average = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=50, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    attributes = models.JSONField(
        default=dict,
        help_text="Dynamic attributes validated against ProductType",
    )
    product_type = models.ForeignKey(
        "ProductType",
        on_delete=models.PROTECT,
        related_name="products",
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["category", "subcategory"]),
            GinIndex(fields=["attributes"]),
        ]

    @property
    def is_in_stock(self) -> bool:
        """Returns True if the product has stock available, False otherwise."""
        return self.stock_quantity > 0

    def _slug_exists(self, slug: str) -> bool:
        """
        Return True if the candidate_slug exists on another instance.
        Excludes this instance (by pk).
        """
        queryset = self.__class__.objects.filter(slug=slug)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        return queryset.exists()

    MAX_SLUG_LENGTH = 100
    TIMESTAMP_LENGTH = 17

    def _generate_base_slug(self, slug: str) -> str:
        """This helper function ensures the length of base slug allows adding timestamp."""
        allowed_length = Product.MAX_SLUG_LENGTH - Product.TIMESTAMP_LENGTH
        if len(slug) > allowed_length:
            truncated = slug[:allowed_length]
            last_dash = truncated.rfind("-")
            if last_dash != -1:
                truncated = truncated[:last_dash]
            return truncated
        return slug

    def _generate_unique_slug(self) -> str:
        slug = slugify(self.name)
        base_slug = self._generate_base_slug(slug)

        while self._slug_exists(slug):
            slug = f"{base_slug}-{time.time()}"
        return slug

    def _validate_attributes(self) -> None:
        """
        Validates self.attributes against the JSON Schema from ProductType.

        Returns:
            None if valid.
        Raises:
            jsonschema.ValidationError: if attributes are invalid
        """
        validate(instance=self.attributes, schema=self.product_type.fields)

    def _sync_categories(self) -> None:
        """
        Sync category/subcategory only if product_type changed or category fields are empty.
        Prevent overwriting manual edits.
        """
        if not self.pk or self.category != self.product_type.category_type:
            self.category = self.product_type.category_type

        if not self.pk or self.subcategory != self.product_type.subcategory_type:
            self.subcategory = self.product_type.subcategory_type

    def clean(self):
        """
        Custom model validation.
        - Prevents a product from being a variant of itself.
        - Ensures variant products have the same ProductType as the parent.
        """
        if self.variant_of and self.variant_of_id == self.id:
            raise DjangoValidationError({"variant_of": "A product cannot be a variant of itself."})

        if self.variant_of and self.variant_of.product_type != self.product_type:
            raise DjangoValidationError({
                "variant_of": "A variant must have the same product type as its parent."
            })

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Save the Product instance.

        - Generates a unique slug if missing or duplicate.
        - Validates `attributes` against `product_type.fields` JSON Schema.
        - Raises `DjangoValidationError` if attributes are invalid.
        - Syncs Product category/subcategory fields with ProductType category/subcategory.
        - Saves the object to the database.
        """
        if not self.slug or self._slug_exists(self.slug):
            self.slug = self._generate_unique_slug()

        try:
            self._validate_attributes()
        except JSONSchemaValidationError as e:
            raise DjangoValidationError({"attributes": e.message}) from e

        self._sync_categories()

        super().save(*args, **kwargs)