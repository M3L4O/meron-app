from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import CPU, GPU, PSU, RAM, CurrentVolatileData, Motherboard, Storage


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
    # A linha que ativa o método get_volatile_data
    volatile_data = serializers.SerializerMethodField()

    class Meta:
        model = CPU
        # Lista explícita de campos para incluir o nosso campo customizado
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
            "volatile_data",  # Adiciona o campo aqui
        ]

    def get_volatile_data(self, obj):
        """
        Busca os dados voláteis para uma instância de componente (CPU, neste caso).
        """
        content_type = ContentType.objects.get_for_model(obj.__class__)
        volatile_items = CurrentVolatileData.objects.filter(
            content_type=content_type, object_id=obj.id
        )
        serializer = CurrentVolatileDataSerializer(volatile_items, many=True)
        return serializer.data


class GPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPU
        fields = "__all__"

    def to_internal_value(self, data):
        data["consumption"] = parse_numeric_value(
            data["consumption"], "W", target_type=int
        )
        data["vram"] = parse_numeric_value(data["vram"], "GB", target_type=float)
        data["vram_speed"] = parse_numeric_value(
            data["vram_speed"], "MHz", target_type=float
        )
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


class CurrentVolatileDataSerializer(serializers.ModelSerializer):
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
