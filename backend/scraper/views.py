from rest_framework import viewsets
from rest_framework import filters
from .models import CPU, GPU, Motherboard, RAM, PSU, Storage, Volatile
from .serializers import CPUSerializer, GPUSerializer, MotherboardSerializer, RAMSerializer, PSUSerializer, StorageSerializer, VolatileSerializer

class CPUViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CPUs to be viewed or edited.
    """
    queryset = CPU.objects.all().order_by(
        "model"
    )  # Busca todos os objetos CPU e os ordena pelo nome
    serializer_class = CPUSerializer  # Usa o CPUSerializer para converter os objetos CPU em JSON
    filter_backends = [filters.SearchFilter]  # Habilita o filtro de busca
    search_fields = ["model", "socket", "integrated_gpu", "manufacturer"]  # Campos pesquisáveis

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

class VolatileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Volatile data to be viewed or edited.
    """
    queryset = Volatile.objects.all().order_by("-timestamp")  # Ordena por timestamp decrescente
    serializer_class = VolatileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["component_type", "component_id"]