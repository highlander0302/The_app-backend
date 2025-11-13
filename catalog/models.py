"""
Product Models Module

This module defines models for managing digital products in an e-commerce marketplace.

Hierarchy Overview:
-------------------
1. Product (abstract)
    - Contains common fields for all products such as:
    name, SKU, price, stock, media, ratings, timestamps, and marketplace-related metadata.

2. Category-level Abstract Models (abstract)
    - ComputingDevice: Common fields for laptops, desktops, tablets (e.g., processor, RAM)
    - MobileDevice: Common fields for smartphones, smartwatches, fitness trackers
    - AudioDevice: Common fields for headphones, speakers
    - ImagingDevice: Common fields for cameras and drones
    - GamingDevice: Common fields for consoles and VR systems
    - NetworkingDevice: Common fields for routers, modems, NAS
    - DigitalGadget: Common fields for other gadgets like e-readers, projectors, digital pens

3. Concrete Product Models
    - Define specific products with unique fields
    (e.g., Laptop, Smartphone, Headphones, DigitalCamera, VRGamingSystem, EReader, etc.)
"""
from typing import Any
import time
from random import randint
from django.db import models
from django.utils.text import slugify


# --- Product (abstract) ---
class Product(models.Model):
    """
    Abstract base model for all digital products in the marketplace.

    Provides common fields for:
    - Identification: id, slug, name, SKU, UPC
    - Descriptions: description, short_description, brand, vendor, category, subcategory, tags
    - Pricing:
    cost_price, retail_price, sale_price, currency, stock_quantity, is_in_stock, stock_threshold
    - Physical attributes:
    weight, dimensions, origin_country, shipping_required, color, size, material, variant_of
    - Media: image_main, images
    - Ratings & reviews: rating_average, review_count
    - Status: is_active, is_featured, approval_status, created_at, updated_at, deleted_at

    Automatically generates a URL-friendly slug from the product name if not provided.
    """
    id = models.BigAutoField(primary_key=True)
    slug = models.SlugField(unique=True, blank=True, max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    brand = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)
    sku = models.CharField(max_length=100, unique=True, verbose_name="Stock Keeping Unit")
    upc = models.CharField(max_length=100, blank=True, verbose_name="Universal Product Code")

    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    stock_quantity = models.IntegerField(default=0)
    stock_threshold = models.IntegerField(default=5)

    weight = models.FloatField(help_text="Weight in grams (g)", null=True, blank=True)
    length = models.FloatField(help_text="Length in centemeters (cm)", null=True, blank=True)
    width = models.FloatField(help_text="With in centemeters (cm)", null=True, blank=True)
    height = models.FloatField(help_text="Height in centemeters (cm)", null=True, blank=True)
    origin_country = models.CharField(max_length=54, blank=True)
    shipping_required = models.BooleanField(default=True)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="screen size in inches / resolution"
    )
    material = models.CharField(max_length=50, blank=True)
    variant_of = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='variants'
    )

    image_main = models.URLField(blank=True)
    images = models.JSONField(default=list, blank=True)

    rating_average = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=50, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def is_in_stock(self) -> bool:
        """Returns True if the product has stock available, False otherwise."""
        return self.stock_quantity > 0

    def _slug_exists(self, slug: str) -> bool:
        """Check if a given slug already exists in the database."""
        return self.__class__.objects.filter(slug=slug).exists()

    def _generate_unique_slug(self) -> str:
        base_slug = slugify(self.name)
        slug = base_slug

        while self._slug_exists(slug):
            slug = f"{base_slug}-{int(time.time())}-{randint(1, 1000)}"

        return slug

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Generates a URL-friendly slug from the product name if not already set.
        (e.g., "Apple MacBook Pro" → "apple-macbook-pro").
        """
        if not self.slug or self._slug_exists(self.slug):
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)


# --- Domain Base Classes (abstract)---
class Computer(Product):
    """Abstract base class for general-purpose computing devices."""
    cpu = models.CharField(max_length=255)
    ram = models.IntegerField(help_text="RAM in GB")
    storage = models.IntegerField(help_text="Storage in GB")
    operating_system = models.CharField(max_length=100)

    class Meta:
        abstract = True


class Appliance(Product):
    """Abstract base class for non-general-purpose devices."""
    class Meta:
        abstract = True


# --- Mixins ---
class BatteryMixin(models.Model):
    battery_capacity = models.IntegerField(
        null=True,
        blank=True,
        help_text="Battery capacity in mAh"
    )
    battery_life = models.IntegerField(null=True, blank=True, help_text="Battery life in hours")

    class Meta:
        abstract = True


class ScreenMixin(models.Model):
    screen_size = models.FloatField(null=True, blank=True, help_text="Screen size in inches")
    resolution = models.CharField(max_length=50, blank=True)
    touch_support = models.BooleanField(default=False)

    class Meta:
        abstract = True


class ConnectivityMixin(models.Model):
    connectivity = models.CharField(
        max_length=100,
        blank=True,
        help_text="WiFi, Bluetooth, Cellular, etc."
    )
    gps = models.BooleanField(default=False)

    class Meta:
        abstract = True


class KeyboardMixin(models.Model):
    keyboard_backlight = models.BooleanField(default=False)

    class Meta:
        abstract = True


class PortsMixin(models.Model):
    usb_ports = models.IntegerField(null=True, blank=True)
    ethernet_ports = models.IntegerField(null=True, blank=True)
    hdmi_ports = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class CameraMixin(models.Model):
    camera_megapixels = models.IntegerField(null=True, blank=True)
    video_resolution = models.CharField(max_length=50, blank=True)
    optical_zoom = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True


class AudioMixin(models.Model):
    is_wireless = models.BooleanField(default=False)
    noise_cancelling = models.BooleanField(default=False)
    microphone = models.BooleanField(default=False)

    class Meta:
        abstract = True


# --- Concrete Product Models ---

# Computers
class Laptop(Computer, BatteryMixin, ScreenMixin, KeyboardMixin, ConnectivityMixin):
    touch_screen = models.BooleanField(default=False)


class Desktop(Computer, KeyboardMixin, PortsMixin):
    form_factor = models.CharField(max_length=50, blank=True)
    gpu_options = models.CharField(max_length=100, blank=True)
    expandable_storage = models.BooleanField(default=True)


class Tablet(Computer, BatteryMixin, ScreenMixin, ConnectivityMixin):
    stylus_support = models.BooleanField(default=False)
    cellular_connectivity = models.BooleanField(default=False)


# Appliances
class Smartphone(Appliance, BatteryMixin, ScreenMixin, ConnectivityMixin, CameraMixin):
    waterproof = models.BooleanField(default=False)
    dual_sim = models.BooleanField(default=False)


class Smartwatch(Appliance, BatteryMixin, ScreenMixin, ConnectivityMixin):
    heart_rate_monitor = models.BooleanField(default=True)
    sleep_tracking = models.BooleanField(default=True)


class FitnessTracker(Appliance, BatteryMixin, ScreenMixin, ConnectivityMixin):
    step_tracking = models.BooleanField(default=True)
    heart_rate_monitor = models.BooleanField(default=True)
    sleep_tracking = models.BooleanField(default=True)


class Headphones(Appliance, BatteryMixin, AudioMixin, ConnectivityMixin):
    pass


class SmartSpeaker(Appliance, AudioMixin, ConnectivityMixin):
    voice_assistant = models.BooleanField(default=True)


class DigitalCamera(Appliance, CameraMixin, BatteryMixin):
    lens_type = models.CharField(max_length=100)


class ActionCamera(Appliance, CameraMixin, BatteryMixin):
    waterproof = models.BooleanField(default=True)
    mount_compatibility = models.CharField(max_length=100)


class Drone(Appliance, BatteryMixin, CameraMixin, ConnectivityMixin):
    flight_time = models.IntegerField(help_text="Flight time in minutes")


class GamingConsole(Appliance, BatteryMixin, ScreenMixin):
    controller_type = models.CharField(max_length=50, blank=True)


class HandheldConsole(Appliance, BatteryMixin, ScreenMixin):
    battery_life = models.IntegerField(null=True, blank=True)


class VRGamingSystem(Appliance, BatteryMixin, ScreenMixin):
    tracking_sensors = models.CharField(max_length=100, blank=True)
    controllers = models.CharField(max_length=100, blank=True)


class Router(Appliance, ConnectivityMixin, PortsMixin):
    number_of_lan_ports = models.IntegerField(null=True, blank=True)
    number_of_wan_ports = models.IntegerField(null=True, blank=True)
    ethernet_port_speed = models.CharField(max_length=50, blank=True)
    band_count = models.IntegerField(null=True, blank=True)
    supports_mu_mimo = models.BooleanField(default=False)
    usb_ports = models.IntegerField(null=True, blank=True)


class Modem(Appliance, ConnectivityMixin, PortsMixin):
    modem_type = models.CharField(max_length=100, blank=True)
    max_downstream_speed = models.CharField(max_length=50, blank=True)
    max_upstream_speed = models.CharField(max_length=50, blank=True)


class EReader(Appliance, BatteryMixin, ScreenMixin, StorageMixin):
    screen_type = models.CharField(max_length=50)


class Projector(Appliance, BatteryMixin, ScreenMixin):
    brightness = models.IntegerField(help_text="Lumens")


class WearableMedicalDevice(Appliance, BatteryMixin, ConnectivityMixin):
    sensor_type = models.CharField(max_length=50)


class DigitalPen(Appliance, ConnectivityMixin):
    compatibility = models.CharField(max_length=50)
    pressure_sensitivity = models.BooleanField(default=True)
