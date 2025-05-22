from rest_framework import serializers
from .models import CPU, GPU, Motherboard, RAM, Storage, PSU, Volatile



class VolatileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volatile
        fields = '__all__'

class CPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPU
        fields = "__all__"


class GPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPU
        fields = "__all__"

    def to_internal_value(self, data):
        if data["consumption"] == "":
            data["consumption"] = 0
        return super().to_internal_value(data)


class MotherboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motherboard
        fields = "__all__"


class RAMSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAM
        fields = "__all__"

    def to_internal_value(self, data):
        if "speed" not in data or data["speed"] is None:
            data["speed"] = 0.0
        return super().to_internal_value(data)


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = "__all__"


class PSUSerializer(serializers.ModelSerializer):
    class Meta:
        model = PSU
        fields = "__all__"

    def to_internal_value(self, data):
        if "rate" not in data or data["rate"] is None:
            data["rate"] = "Não especificado"
        return super().to_internal_value(data)
