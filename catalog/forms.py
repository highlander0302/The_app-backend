from django import forms

from catalog.models import Product


class ProductAdminForm(forms.ModelForm):
    """
    Django admin form for Product. Exposes all fields and ensures attributes JSON is entered.
    """

    attributes = forms.JSONField(
        required=True,
        help_text="JSON object matching the product type attributes schema.",
    )

    class Meta:
        model = Product
        fields = "__all__"
