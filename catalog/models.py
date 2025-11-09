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

    #TODO: utilize Pillow for image processing later
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
        """
        Returns True if the product has stock available, False otherwise.
        """
        return self.stock_quantity > 0

    def _generate_unique_slug(self) -> str:
        base_slug = slugify(self.name)
        model_class = self.__class__

        if not model_class.objects.filter(slug=base_slug).exists():
            return base_slug

        timestamp_suffix = str(int(time.time()))
        return f"{base_slug}-{timestamp_suffix}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Generates a URL-friendly slug from the product name if not already set.
        (e.g., "Apple MacBook Pro" → "apple-macbook-pro").
        """
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)


# --- Category-level Models (abstract) ---
class ComputingDevice(Product):
    """
    Abstract model for computing devices (laptops, tablets, phones, etc.).
    """
    processor = models.CharField(max_length=255)
    ram = models.IntegerField(help_text="RAM in GB")
    storage = models.IntegerField(help_text="Storage in GB")
    operating_system = models.CharField(max_length=100)
    screen_size = models.FloatField(help_text="Screen size in inches", null=True, blank=True)

    class Meta:
        abstract = True


class MobileDevice(Product):
    """
    Abstract model for mobile devices (smartphones, smartwatches, etc.).
    """
    operating_system = models.CharField(max_length=100)
    battery_capacity = models.IntegerField(help_text="Battery capacity in mAh")
    screen_size = models.FloatField(help_text="Screen size in inches")
    connectivity = models.CharField(max_length=100, help_text="4G, 5G, Wi-Fi, Bluetooth")

    class Meta:
        abstract = True


class AudioDevice(Product):
    """
    Abstract model for audio devices (headphones, speakers, etc.).
    """
    battery_life = models.IntegerField(help_text="Battery life in hours", null=True, blank=True)
    connectivity = models.CharField(max_length=100, blank=True)
    is_wireless = models.BooleanField(default=False)

    class Meta:
        abstract = True


class ImagingDevice(Product):
    """
    Abstract model for imaging devices (cameras, camcorders, etc.).
    """
    resolution = models.CharField(max_length=50)
    sensor_type = models.CharField(max_length=50, null=True, blank=True)
    optical_zoom = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True


class GamingDevice(Product):
    """
    Abstract model for gaming devices (laptops, consoles, handhelds).
    """
    gpu = models.CharField(max_length=100, blank=True)
    storage_options = models.CharField(max_length=100, blank=True)
    screen_size = models.FloatField(null=True, blank=True)
    battery_life = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class NetworkingDevice(Product):
    """
    Abstract model for networking devices (routers, switches, access points).
    """
    wifi_standard = models.CharField(max_length=50, blank=True)
    ports = models.JSONField(default=list, blank=True)
    max_devices = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class DigitalGadget(Product):
    """
    Abstract model for general digital gadgets (smartwatches, fitness trackers, etc.).
    """
    battery_life = models.IntegerField(null=True, blank=True)
    connectivity = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True


# --- Concrete Product Models ---
class Laptop(ComputingDevice):
    """Concrete model for laptops."""
    battery_life = models.IntegerField(help_text="Battery life in hours")
    keyboard_backlight = models.BooleanField(default=False)
    touch_screen = models.BooleanField(default=False)


class Desktop(ComputingDevice):
    """Concrete model for desktop computers."""
    form_factor = models.CharField(max_length=50, blank=True)
    gpu_options = models.CharField(max_length=100, blank=True)
    expandable_storage = models.BooleanField(default=True)


class Tablet(ComputingDevice):
    """Concrete model for tablets."""
    stylus_support = models.BooleanField(default=False)
    cellular_connectivity = models.BooleanField(default=False)
    battery_life = models.IntegerField(help_text="Battery life in hours", null=True, blank=True)


class Smartphone(MobileDevice):
    """Concrete model for smartphones."""
    camera_megapixels = models.IntegerField()
    dual_sim = models.BooleanField(default=False)
    waterproof = models.BooleanField(default=False)


class Smartwatch(MobileDevice):
    """Concrete model for smartwatches."""
    heart_rate_monitor = models.BooleanField(default=True)
    sleep_tracking = models.BooleanField(default=True)
    gps = models.BooleanField(default=False)


class FitnessTracker(MobileDevice):
    """Concrete model for fitness trackers."""
    step_tracking = models.BooleanField(default=True)
    heart_rate_monitor = models.BooleanField(default=True)
    sleep_tracking = models.BooleanField(default=True)


class Headphones(AudioDevice):
    """Concrete model for headphones."""
    noise_cancelling = models.BooleanField(default=False)
    microphone = models.BooleanField(default=True)


class SmartSpeaker(AudioDevice):
    """Concrete model for smart speakers."""
    voice_assistant = models.BooleanField(default=True)


class DigitalCamera(ImagingDevice):
    """Concrete model for digital cameras."""
    lens_type = models.CharField(max_length=100)
    video_resolution = models.CharField(max_length=50)


class ActionCamera(ImagingDevice):
    """Concrete model for action cameras."""
    waterproof = models.BooleanField(default=True)
    mount_compatibility = models.CharField(max_length=100)
    video_resolution = models.CharField(max_length=50)


class Drone(ImagingDevice):
    """Concrete model for drones."""
    flight_time = models.IntegerField(help_text="Flight time in minutes")
    gps = models.BooleanField(default=True)


class GamingConsole(GamingDevice):
    """Concrete model for gaming consoles."""
    controller_type = models.CharField(max_length=50, blank=True)


class HandheldConsole(GamingDevice):
    """Concrete model for handheld consoles."""
    battery_life = models.IntegerField(null=True, blank=True)


class VRGamingSystem(GamingDevice):
    """Concrete model for VR taming systems."""
    tracking_sensors = models.CharField(max_length=100, blank=True)
    controllers = models.CharField(max_length=100, blank=True)


class Router(NetworkingDevice):
    """Concrete model for routers. """
    number_of_lan_ports = models.IntegerField(null=True, blank=True)
    number_of_wan_ports = models.IntegerField(null=True, blank=True)
    ethernet_port_speed = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., '1 Gbps', '2.5 Gbps'",
    )
    band_count = models.IntegerField(
        null=True, blank=True,
        help_text="Number of frequency bands, e.g., 2 for dual‑band, 3 for tri‑band",
    )
    supports_mu_mimo = models.BooleanField(default=False)
    usb_ports = models.IntegerField(null=True, blank=True)


class Modem(NetworkingDevice):
    """Concrete model for routers."""
    modem_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., ADSL2+, VDSL2, DOCSIS3.1",
        )
    max_downstream_speed = models.CharField(max_length=50, blank=True, help_text="e.g., '1 Gbps'")
    max_upstream_speed = models.CharField(max_length=50, blank=True)


class NAS(NetworkingDevice):
    """Concrete model for Network Attached Storage (NAS) devices."""
    drive_bays = models.IntegerField(null=True, blank=True)
    max_storage_capacity_tb = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum supported storage in TB",
    )
    supported_raid_levels = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., RAID0, RAID1, RAID5",
    )

    class Meta:
        verbose_name = "Network Attached Storage (NAS)"


class EReader(DigitalGadget):
    """Concrete model for EReaders."""
    screen_type = models.CharField(max_length=50)
    storage = models.IntegerField(help_text="Storage in GB")


class Projector(DigitalGadget):
    """Concrete model for projectors."""
    resolution = models.CharField(max_length=50)
    brightness = models.IntegerField(help_text="Lumens")


class WearableMedicalDevice(DigitalGadget):
    """Concrete model for projectors."""
    sensor_type = models.CharField(max_length=50)
    connectivity = models.CharField(max_length=50)


class DigitalPen(DigitalGadget):
    """Concrete model for projectors."""
    compatibility = models.CharField(max_length=50)
    pressure_sensitivity = models.BooleanField(default=True)
