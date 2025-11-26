from django.contrib import admin
from django.db.models import JSONField
from django.forms import Textarea

from catalog.forms import ProductAdminForm
from catalog.models import Product, ProductType


class VariantInline(admin.TabularInline):
    """
    Interface for adding variants of a product in the end of Product creation form.
    """

    model = Product
    fk_name = "variant_of"
    extra = 1
    fields = ("name", "sku", "sale_price", "stock_quantity", "is_active", "slug")
    readonly_fields = ("slug",)
    verbose_name = "Product Variant (Optional)"
    verbose_name_plural = "Product Variants (Optional)"


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    """Admin for ProductType class that contains JSON schema falidation rules."""

    list_display = ("name", "category_type", "subcategory_type", "created_at")
    search_fields = ("name", "category_type", "subcategory_type")
    ordering = ("name",)
    formfield_overrides = {JSONField: {"widget": Textarea(attrs={"rows": 6, "cols": 60})}}

    def __str__(self) -> str:
        return self.name


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for managing concrete products, including variants and attributes."""

    form = ProductAdminForm

    list_display = (
        "name",
        "sku",
        "is_in_stock",
        "stock_quantity",
        "sale_price",
        "is_active",
        "approval_status",
    )
    list_filter = ("is_active", "approval_status", "_category")
    search_fields = ("name", "sku", "brand", "vendor")
    raw_id_fields = ("product_type", "variant_of")
    inlines = [VariantInline]
    readonly_fields = ("slug", "_category", "_subcategory", "created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                    "product_type",
                    "variant_of",
                    "sku",
                    "upc",
                    "brand",
                    "vendor",
                )
            },
        ),
        (
            "Product Details",
            {
                "fields": (
                    "description",
                    "short_description",
                    "origin_country",
                    "shipping_required",
                    "color",
                    "product_size",
                    "material",
                )
            },
        ),
        (
            "Pricing & Stock",
            {
                "fields": (
                    "retail_price",
                    "sale_price",
                    "cost_price",
                    "currency",
                    "stock_quantity",
                    "stock_threshold",
                )
            },
        ),
        ("Dimensions", {"fields": ("weight", "length", "width", "height")}),
        ("Identifiers", {"fields": ("tags", "image_main", "images")}),
        ("Attributes (JSON)", {"fields": ("attributes",)}),
        ("Status", {"fields": ("is_active", "is_featured", "approval_status")}),
    )
