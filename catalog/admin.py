from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import (
    ActionCamera,
    Desktop,
    DigitalCamera,
    DigitalPen,
    Drone,
    EReader,
    FitnessTracker,
    GamingConsole,
    HandheldConsole,
    Headphones,
    Laptop,
    Modem,
    Projector,
    Router,
    Smartphone,
    SmartSpeaker,
    Smartwatch,
    Tablet,
    VRGamingSystem,
    WearableMedicalDevice,
)


@admin.register(Laptop)
class LaptopAdmin(ModelAdmin):
    pass


@admin.register(Desktop)
class DesktopAdmin(ModelAdmin):
    pass


@admin.register(Tablet)
class TabletAdmin(ModelAdmin):
    pass


# Appliances
@admin.register(Smartphone)
class SmartphoneAdmin(ModelAdmin):
    pass


@admin.register(Smartwatch)
class SmartwatchAdmin(ModelAdmin):
    pass


@admin.register(FitnessTracker)
class FitnessTrackerAdmin(ModelAdmin):
    pass


@admin.register(Headphones)
class HeadphonesAdmin(ModelAdmin):
    pass


@admin.register(SmartSpeaker)
class SmartSpeakerAdmin(ModelAdmin):
    pass


@admin.register(DigitalCamera)
class DigitalCameraAdmin(ModelAdmin):
    pass


@admin.register(ActionCamera)
class ActionCameraAdmin(ModelAdmin):
    pass


@admin.register(Drone)
class DroneAdmin(ModelAdmin):
    pass


@admin.register(GamingConsole)
class GamingConsoleAdmin(ModelAdmin):
    pass


@admin.register(HandheldConsole)
class HandheldConsoleAdmin(ModelAdmin):
    pass


@admin.register(VRGamingSystem)
class VRGamingSystemAdmin(ModelAdmin):
    pass


@admin.register(Router)
class RouterAdmin(ModelAdmin):
    pass


@admin.register(Modem)
class ModemAdmin(ModelAdmin):
    pass


@admin.register(EReader)
class EReaderAdmin(ModelAdmin):
    pass


@admin.register(Projector)
class ProjectorAdmin(ModelAdmin):
    pass


@admin.register(WearableMedicalDevice)
class WearableMedicalDeviceAdmin(ModelAdmin):
    pass


@admin.register(DigitalPen)
class DigitalPenAdmin(ModelAdmin):
    pass
