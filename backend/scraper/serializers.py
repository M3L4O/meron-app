from rest_framework import serializers
from .models import CPU, GPU, Motherboard, RAM, Storage, PSU


def parse_numeric_value(value_str, unit, target_type=float):
    """
    Tenta converter uma string que contém um valor numérico e uma unidade
    para um tipo numérico (int ou float).

    Args:
        value_str (str): A string original (ex: "100W", "8GB", "1500MHz").
        unit (str): A unidade a ser removida da string (ex: "W", "GB", "MHz").
        target_type (type): O tipo numérico desejado (int ou float).

    Returns:
        int/float: O valor numérico convertido, ou 0 se a conversão falhar.
    """
    if isinstance(value_str, (int, float)):
        return target_type(value_str)  
    if not isinstance(value_str, str):
        return 0  

    clean_value_str = value_str.replace(unit, "").strip()
    try:
        if clean_value_str.isdigit() and target_type == int:
            return int(clean_value_str)
        else:
            return target_type(clean_value_str)
    except ValueError:
        return 0
    except AttributeError:
        return 0


class CPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPU
        fields = "__all__"


class GPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPU
        fields = "__all__"

    def to_internal_value(self, data):
        data["consumption"] = parse_numeric_value(data["consumption"], "W", target_type=int)
        data["vram"] = parse_numeric_value(data["vram"], "GB", target_type=float)
        data["vram_speed"] = parse_numeric_value(data["vram_speed"], "MHz", target_type=float)
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
