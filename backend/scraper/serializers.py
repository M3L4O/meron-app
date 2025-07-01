from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import CPU, GPU, PSU, RAM, CurrentVolatileData, Motherboard, Storage


class CurrentVolatileDataSerializer(serializers.ModelSerializer):
    last_checked = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)

    class Meta:
        model = CurrentVolatileData
        fields = [
            "product_name_on_source",
            "url",
            "source",
            "current_price",
            "current_availability",
            "last_checked",
        ]


class VolatileDataMixin(serializers.Serializer):
    volatile_data = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

    def get_volatile_data(self, obj):
        if "volatile_list" in self.context:
            volatile_items = self.context["volatile_list"]
        else:
            volatile_map = self.context.get("volatile_map", {})
            volatile_items = volatile_map.get(obj.id, [])
        return CurrentVolatileDataSerializer(volatile_items, many=True).data

    def get_price(self, obj):
        if "volatile_list" in self.context:
            volatile_items = self.context["volatile_list"]
        else:
            volatile_map = self.context.get("volatile_map", {})
            volatile_items = volatile_map.get(obj.id, [])

        available_offers = [o for o in volatile_items if o.current_availability]
        if not available_offers:
            return None

        best_price_offer = min(available_offers, key=lambda o: o.current_price)
        return best_price_offer.current_price

    def get_availability(self, obj):
        if "volatile_list" in self.context:
            volatile_items = self.context["volatile_list"]
        else:
            volatile_map = self.context.get("volatile_map", {})
            volatile_items = volatile_map.get(obj.id, [])

        is_available = any(o.current_availability for o in volatile_items)
        return "Em estoque" if is_available else "Indisponível"


class CPUSerializer(VolatileDataMixin, serializers.ModelSerializer):
    class Meta:
        model = CPU
        fields = [
            "id",
            "manufacturer",
            "model",
            "socket",
            "n_cores",
            "base_clock_speed",
            "boost_clock_speed",
            "consumption",
            "integrated_gpu",
            "volatile_data",
            "price",
            "availability",
        ]


class GPUSerializer(VolatileDataMixin, serializers.ModelSerializer):
    class Meta:
        model = GPU
        fields = [
            "id",
            "manufacturer",
            "model",
            "chipset",
            "vram",
            "base_clock_speed",
            "boost_clock_speed",
            "consumption",
            "volatile_data",
            "price",
            "availability",
        ]


class MotherboardSerializer(VolatileDataMixin, serializers.ModelSerializer):
    class Meta:
        model = Motherboard
        fields = [
            "id",
            "manufacturer",
            "model",
            "socket",
            "board_size",
            "n_ram_slots",
            "memory_gen",
            "memory_max",
            "memory_speeds",
            "sata",
            "m2",
            "pcie_x1",
            "pcie_x4",
            "pcie_x8",
            "pcie_x16",
            "usb",
            "volatile_data",
            "price",
            "availability",
        ]


class RAMSerializer(VolatileDataMixin, serializers.ModelSerializer):
    class Meta:
        model = RAM
        fields = [
            "id",
            "manufacturer",
            "model",
            "generation",
            "size",
            "speed",
            "volatile_data",
            "price",
            "availability",
        ]


class StorageSerializer(VolatileDataMixin, serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = [
            "id",
            "manufacturer",
            "model",
            "capacity",
            "io",
            "is_hdd",
            "rpm",
            "volatile_data",
            "price",
            "availability",
        ]


class PSUSerializer(VolatileDataMixin, serializers.ModelSerializer):
    class Meta:
        model = PSU
        fields = [
            "id",
            "manufacturer",
            "model",
            "power",
            "rate",
            "volatile_data",
            "price",
            "availability",
        ]
