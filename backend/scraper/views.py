from rest_framework import viewsets
from rest_framework import filters
from .models import CPU, GPU, Motherboard, RAM, PSU, Storage, CurrentVolatileData
from .serializers import (
    CPUSerializer,
    GPUSerializer,
    MotherboardSerializer,
    RAMSerializer,
    PSUSerializer,
    StorageSerializer,
)
from django.db.models import Exists, OuterRef
from django.contrib.contenttypes.models import ContentType


class CPUViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite que as CPUs sejam vistas ou editadas.
    Com busca e ordenação por dados voláteis.
    """
    queryset = CPU.objects.all()

    serializer_class = CPUSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["model", "socket", "integrated_gpu", "manufacturer"]

    def get_queryset(self):
        """
        Define o queryset base, já com a anotação e ordenação.
        O filtro de busca será aplicado sobre este resultado pelo DRF.
        """
        cpu_content_type = ContentType.objects.get_for_model(CPU)

        volatile_data_exists = CurrentVolatileData.objects.filter(
            content_type=cpu_content_type, object_id=OuterRef("pk")
        )

        # A nossa query base com a anotação e ordenação
        queryset = CPU.objects.annotate(
            has_volatile_data=Exists(volatile_data_exists)
        ).order_by("-has_volatile_data", "manufacturer", "model")

        return queryset


class GPUViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows GPUs to be viewed or edited.
    """

    queryset = GPU.objects.all().order_by("model")
    serializer_class = GPUSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["model", "chipset", "vram", "manufacturer"]


class MotherboardViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Motherboards to be viewed or edited.
    """

    queryset = Motherboard.objects.all().order_by("model")
    serializer_class = MotherboardSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["model", "socket", "chipset", "form_factor", "manufacturer"]


class RAMViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows RAMs to be viewed or edited.
    """

    queryset = RAM.objects.all().order_by("model")
    serializer_class = RAMSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["model", "memory_type", "capacity", "frequency", "manufacturer"]


class PSUViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows PSUs to be viewed or edited.
    """

    queryset = PSU.objects.all().order_by("model")
    serializer_class = PSUSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["model", "wattage", "efficiency_rating", "manufacturer"]


class StorageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Storages to be viewed or edited.
    """

    queryset = Storage.objects.all().order_by("model")
    serializer_class = StorageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["model", "storage_type", "capacity", "manufacturer"]
