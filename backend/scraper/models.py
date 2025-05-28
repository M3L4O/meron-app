from uuid import uuid4
from django.utils import timezone

from django.db import models
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
)
from django.contrib.contenttypes.models import ContentType


class CPU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(unique=True, max_length=255, blank=False, null=False)
    socket = models.CharField(max_length=50, blank=False, null=False)
    n_cores = models.IntegerField()
    base_clock_speed = models.FloatField()
    boost_clock_speed = models.FloatField()
    consumption = models.IntegerField()
    integrated_gpu = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.model


class GPU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=False, null=False)
    consumption = models.IntegerField()
    vram = models.FloatField()  # GB
    vram_speed = models.FloatField()  # MHz

    def __str__(self):
        return self.model


class Motherboard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=False, null=False)
    socket = models.CharField(max_length=50, blank=False, null=False)
    board_size = models.CharField(max_length=50, blank=False, null=False)
    n_ram_slots = models.IntegerField()
    memory_gen = models.CharField(max_length=50, blank=False, null=False)
    memory_max = models.IntegerField()
    memory_speeds = models.CharField(max_length=400, blank=False, null=False)
    sata = models.IntegerField()
    m2 = models.IntegerField()
    pcie_x1 = models.IntegerField()
    pcie_x4 = models.IntegerField()
    pcie_x8 = models.IntegerField()
    pcie_x16 = models.IntegerField()
    usb = models.IntegerField()

    def __str__(self):
        return self.model


class RAM(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=False, null=False)
    generation = models.CharField(max_length=50, blank=False, null=False)
    size = models.IntegerField()
    speed = models.FloatField()

    def __str__(self):
        return self.model


class Storage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=False, null=False)
    capacity = models.IntegerField()
    io = models.CharField(max_length=50, blank=False, null=False)
    is_hdd = models.BooleanField()
    rpm = models.IntegerField()

    def __str__(self):
        return self.model


class PSU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=False, null=False)
    power = models.IntegerField()
    rate = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.model


class CurrentVolatileData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField(blank=True, null=True)
    component = GenericForeignKey("content_type", "object_id")

    product_name_on_source = models.CharField(
        max_length=500, help_text="Nome do produto como aparece na fonte original"
    )
    url = models.CharField(
        max_length=500,
        blank=False,
        null=False,
        unique=True,
        help_text="URL única do produto na fonte original",
    )
    source = models.CharField(
        max_length=100, blank=False, null=False, help_text="Nome da loja ou fonte"
    )

    current_price = models.FloatField()
    current_availability = models.BooleanField()
    last_checked = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Dado Volátil Atual"
        verbose_name_plural = "Dados Voláteis Atuais"
        unique_together = (
            "url",
            "source",
        )

    def __str__(self):
        component_name = (
            self.component.model if self.component else "N/A (Componente não ligado)"
        )
        return f"Atual: {component_name} ({self.source}) - ${self.current_price} - URL: {self.url}"


class VolatileDataHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)

    current_data_item = models.ForeignKey(
        CurrentVolatileData, on_delete=models.CASCADE, related_name="history"
    )

    product_name_on_source = models.CharField(max_length=500, blank=False, null=False)
    price = models.FloatField()
    availability = models.BooleanField()
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Histórico de Dado Volátil"
        verbose_name_plural = "Histórico de Dados Voláteis"
        ordering = ["-recorded_at"]

    def __str__(self):
        component_name = (
            self.current_data_item.component.model
            if self.current_data_item.component
            else "N/A"
        )
        return (
            f"Histórico para {component_name} ({self.current_data_item.source}) "
            f"- ${self.price} em {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"
        )
