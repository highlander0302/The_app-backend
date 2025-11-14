"""
Product Models Module

This module defines models for managing digital products in an e-commerce marketplace.

Hierarchy Overview:
-------------------
1. Category
    - Represents hierarchical grouping of products.
    - Supports parent-child relationships (subcategories) via a self-referential foreign key.
    - Generates URL-friendly slugs automatically from the category name.
    - Deletion of a category with existing products is **protected** (on_delete=PROTECT).
    - Subcategories inherit the hierarchy display in string representation.
    
2. Product (abstract)
    - Provides common fields for all products such as:
      identification, descriptions, pricing, stock, physical attributes,
      media, ratings, and status metadata.
    - Handles slug generation for unique URL-friendly identifiers.
    - Includes a `stock_threshold` field to notify when inventory falls below the threshold.
    - Supports variants via self-referencing foreign key (`variant_of`) with `SET_NULL` on deletion.
    
3. Domain Base Classes (abstract)
    - Computer: Represents general-purpose computing devices capable of running
      arbitrary software and supporting multiple user applications.
      Examples: laptops, desktops, tablets.
    - Appliance: Represents specialized devices or gadgets designed for a dedicated
      function rather than general-purpose computing.
      Examples: smartwatches, fitness trackers, routers, cameras, projectors.

4. Mixins (abstract)
    - BatteryMixin: Adds battery-related functionality.
    - ScreenMixin: Adds display capabilities.
    - ConnectivityMixin: Adds network and device connectivity features.
    - KeyboardMixin: Adds keyboard-related features.
    - PortsMixin: Adds physical port capabilities.
    - CameraMixin: Adds imaging capabilities.
    - AudioMixin: Adds audio-related functionality.
    - StorageMixin: Adds storage capacity functionality.
    - (Additional mixins can be added to encapsulate other cross-cutting traits.)

5. Concrete Product Models
    - Built by combining a domain base class (Computer or Appliance) with
      relevant mixins to represent specific products.
    - Examples include: Laptop, Smartphone, DigitalCamera, Drone, VRGamingSystem,
      EReader, Projector, DigitalPen, Router, Modem, Headphones, SmartSpeaker.

Usage Note:
-----------
To create a new product, extend either the `Computer` or `Appliance` abstract class, 
and optionally include any relevant mixins (e.g., BatteryMixin, ScreenMixin, ConnectivityMixin) 
to add specific features.
"""
from typing import Any
import time
from random import randint
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children'
    )

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Generates a URL-friendly slug from the category name.
        (e.g., "Gaming Consoles" → "gaming-consoles").
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self) -> str:
        if self.parent:
            return f"{self.parent} → {self.name}"
        return self.name


# --- Product (abstract) ---
class Product(models.Model):
    """
    Abstract base model for all digital products in the marketplace.

    Provides common fields for:
    - Identification: id, slug, name, SKU, UPC
    - Descriptions: description, short_description, brand, vendor, category, tags
    - Pricing:
    cost_price, retail_price, sale_price, currency, stock_quantity, is_in_stock, stock_threshold
    - Physical attributes:
    weight, dimensions, origin_country, shipping_required, color, product_size, material, variant_of
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
    category = models.ForeignKey(
        Category,
        null = True,
        blank = True,
        on_delete=models.PROTECT,
        related_name="products",
    )
    tags = models.JSONField(default=list, blank=True)
    sku = models.CharField(max_length=100, unique=True, verbose_name="Stock Keeping Unit")
    upc = models.CharField(max_length=100, blank=True, verbose_name="Universal Product Code")

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
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
    currency = models.CharField(max_length=3, default='USD')
    stock_quantity = models.IntegerField(default=0)
    stock_threshold = models.IntegerField(default=5)

    weight = models.FloatField(help_text="Weight in grams (g)", null=True, blank=True)
    length = models.FloatField(help_text="Length in centimeters (cm)", null=True, blank=True)
    width = models.FloatField(help_text="Width in centimeters (cm)", null=True, blank=True)
    height = models.FloatField(help_text="Height in centimeters (cm)", null=True, blank=True)
    origin_country = models.CharField(max_length=54, blank=True)
    shipping_required = models.BooleanField(default=True)
    color = models.CharField(max_length=50, blank=True)
    product_size = models.CharField(
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
    """
    Abstract base class representing general-purpose computing devices.

    These devices are capable of running arbitrary software,
    performing computations, and supporting multiple user applications.
    Examples include laptops, desktops, and tablets.
    """
    cpu = models.CharField(max_length=255)
    ram = models.IntegerField(help_text="RAM in GB")
    operating_system = models.CharField(max_length=100)

    class Meta:
        abstract = True


class Appliance(Product):
    """
    Abstract base class representing specialized digital devices or gadgets.

    These devices are purpose-specific, typically running embedded software
    to perform dedicated functions rather than general-purpose computing.
    Examples include smartwatches, fitness trackers, routers, cameras, and projectors.
    """
    class Meta:
        abstract = True


# --- Mixins ---
class BatteryMixin(models.Model):
    """Adds battery-related functionality to a product."""
    battery_capacity = models.IntegerField(
        null=True,
        blank=True,
        help_text="Battery capacity in mAh",
    )
    battery_life = models.IntegerField(null=True, blank=True, help_text="Battery life in hours")

    class Meta:
        abstract = True


class ScreenMixin(models.Model):
    """
    Adds display capabilities to a product.

    screen_size (float): The physical diagonal size of the screen in inches.
        This measures the actual size of the display panel.
    resolution (str): The number of pixels on the display, usually expressed as
        width x height (e.g., '1920x1080'). Higher resolution means more detail
        can be shown on the screen, independent of its physical size.
    """
    screen_size = models.FloatField(null=True, blank=True, help_text="Screen size in inches")
    resolution = models.CharField(
        max_length=50,
        blank=True,
        help_text="Resolution is width x height in pixels (e.g., '1920x1080')."
    )
    touch_support = models.BooleanField(default=False)

    class Meta:
        abstract = True


class ConnectivityMixin(models.Model):
    """Adds network and device connectivity capabilities."""
    connectivity = models.CharField(
        max_length=100,
        blank=True,
        help_text="WiFi, Bluetooth, Cellular, etc.",
    )
    gps = models.BooleanField(default=False)

    class Meta:
        abstract = True


class KeyboardMixin(models.Model):
    """Adds keyboard-related features to a product."""
    keyboard_backlight = models.BooleanField(default=False)

    class Meta:
        abstract = True


class PortsMixin(models.Model):
    """Adds physical port capabilities to a product."""
    usb_ports = models.IntegerField(null=True, blank=True)
    ethernet_ports = models.IntegerField(null=True, blank=True)
    hdmi_ports = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class CameraMixin(models.Model):
    """Adds imaging capabilities to a product."""
    camera_megapixels = models.IntegerField(null=True, blank=True)
    video_resolution = models.CharField(max_length=50, blank=True)
    optical_zoom = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True


class AudioMixin(models.Model):
    """Adds audio-related functionality to a product."""
    is_wireless = models.BooleanField(default=False)
    noise_cancelling = models.BooleanField(default=False)
    microphone = models.BooleanField(default=False)

    class Meta:
        abstract = True


class StorageMixin(models.Model):
    """Adds storage capacity to a product."""
    storage = models.IntegerField(
        help_text="Storage capacity in GB",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


# --- Concrete Product Models ---
# Computers
class Laptop(Computer, BatteryMixin, ScreenMixin, KeyboardMixin, ConnectivityMixin):
    touch_screen = models.BooleanField(default=False)


class Desktop(Computer, KeyboardMixin, PortsMixin):
    """Represents a stationary personal computer designed for office or home use."""
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
    pass

class VRGamingSystem(Appliance, BatteryMixin, ScreenMixin):
    """
    Represents a virtual reality gaming system designed.

    Includes features for motion tracking, visual display, and controller input.
    Typically used with VR headsets and handheld controllers to interact with virtual environments.
    """
    tracking_sensors = models.CharField(max_length=100, blank=True)
    controllers = models.CharField(max_length=100, blank=True)


class Router(Appliance, ConnectivityMixin, PortsMixin):
    number_of_lan_ports = models.IntegerField(null=True, blank=True)
    number_of_wan_ports = models.IntegerField(null=True, blank=True)
    ethernet_port_speed = models.CharField(max_length=50, blank=True)
    band_count = models.IntegerField(null=True, blank=True)
    supports_mu_mimo = models.BooleanField(default=False)


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
