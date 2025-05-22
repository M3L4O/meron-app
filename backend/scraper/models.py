from uuid import uuid4

from django.db import models


class CPU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=False, null=False)
    socket = models.CharField(max_length=50, blank=False, null=False)
    n_cores = models.IntegerField()
    base_clock_speed = models.FloatField()
    boost_clock_speed = models.FloatField()
    consumption = models.IntegerField()
    integrated_gpu = models.CharField(max_length=50, blank=True, null=True)


class GPU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=False, null=False)
    consumption = models.IntegerField()
    vram = models.FloatField()
    vram_speed = models.FloatField()


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


class RAM(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=False, null=False)
    generation = models.CharField(max_length=50, blank=False, null=False)
    size = models.IntegerField()
    speed = models.FloatField()


class Storage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=False, null=False)
    capacity = models.IntegerField()
    io = models.CharField(max_length=50, blank=False, null=False)
    is_hdd = models.BooleanField()
    rpm = models.IntegerField()


class PSU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=False, null=False)
    power = models.IntegerField()
    rate = models.CharField(max_length=50, blank=False, null=False)


class Volatile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    
    url = models.CharField(max_length=255, blank=False, null=False)
    model = models.CharField(max_length=255, blank=False, null=False)
    price = models.FloatField()
    availability = models.BooleanField()
    kind = models.CharField(max_length=50, blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
