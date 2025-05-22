from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets

from .filters import VolatileFilter
from .models import CPU, GPU, PSU, RAM, Motherboard, Storage, Volatile
from .serializers import (
    CPUSerializer,
    GPUSerializer,
    MotherboardSerializer,
    PSUSerializer,
    RAMSerializer,
    StorageSerializer,
    VolatileSerializer,
)


class CPUViewSet(viewsets.ModelViewSet):
    queryset = CPU.objects.all()
    serializer_class = CPUSerializer


class GPUViewSet(viewsets.ModelViewSet):
    queryset = GPU.objects.all()
    serializer_class = GPUSerializer


class MotherboardViewSet(viewsets.ModelViewSet):
    queryset = Motherboard.objects.all()
    serializer_class = MotherboardSerializer


class RAMViewSet(viewsets.ModelViewSet):
    queryset = RAM.objects.all()
    serializer_class = RAMSerializer


class StorageViewSet(viewsets.ModelViewSet):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer


class PSUViewSet(viewsets.ModelViewSet):
    queryset = PSU.objects.all()
    serializer_class = PSUSerializer


class VolatileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Volatile.objects.all()
    serializer_class = VolatileSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VolatileFilter