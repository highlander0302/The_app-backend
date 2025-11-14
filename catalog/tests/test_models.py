import pytest

from catalog.models import Laptop


@pytest.mark.django_db
def test_in_stock() -> None:
    """
    Test that `is_in_stock()` returns True when the product stock is greater than zero.
    """
    product = Laptop.objects.create(
        name="Widget",
        cost_price=10.0,
        stock_quantity=5,
        retail_price=600.0,
        ram=5,
    )
    assert product.is_in_stock


@pytest.mark.django_db
def test_is_in_stock_true() -> None:
    """Test is_in_stock returns False when stock_quantity = 0."""
    laptop = Laptop.objects.create(
        name="Laptop A",
        sku="SKU001",
        brand="BrandA",
        vendor="VendorA",
        category="Computers",
        cost_price=500.0,
        retail_price=600.0,
        cpu="i5",
        ram=8,
        operating_system="Windows 11",
        stock_quantity=0,
    )
    assert laptop.is_in_stock is False
