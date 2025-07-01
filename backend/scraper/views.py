from collections import defaultdict

from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef
from rest_framework import filters, pagination, viewsets
from rest_framework.response import Response

from .models import CPU, GPU, PSU, RAM, CurrentVolatileData, Motherboard, Storage
from .serializers import (
    CPUSerializer,
    GPUSerializer,
    MotherboardSerializer,
    PSUSerializer,
    RAMSerializer,
    StorageSerializer,
)


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100


class BaseComponentViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["model", "manufacturer"]

    def get_queryset(self):
        """
        Responsável APENAS pela ordenação inteligente.
        """
        model_class = self.queryset.model

        volatile_exists_subquery = CurrentVolatileData.objects.filter(
            object_id=OuterRef("pk"),
            content_type=ContentType.objects.get_for_model(model_class),
            current_availability=True,
        )

        queryset = model_class.objects.annotate(
            has_volatile_data=Exists(volatile_exists_subquery)
        )

        queryset = queryset.order_by("-has_volatile_data", "model")

        return queryset

    def list(self, request, *args, **kwargs):
        """
        Responsável pela busca otimizada (prefetch manual) para a lista.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            model_class = self.queryset.model
            model_content_type = ContentType.objects.get_for_model(model_class)
            object_ids = [item.id for item in page]

            volatile_data_qs = CurrentVolatileData.objects.filter(
                content_type=model_content_type, object_id__in=object_ids
            )

            volatile_map = defaultdict(list)
            for volatile_item in volatile_data_qs:
                volatile_map[volatile_item.object_id].append(volatile_item)

            serializer_context = {"request": request, "volatile_map": volatile_map}
            serializer = self.get_serializer(
                page, many=True, context=serializer_context
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Responsável por buscar os dados para a página de detalhes.
        """
        instance = self.get_object()

        content_type = ContentType.objects.get_for_model(instance.__class__)
        volatile_items = CurrentVolatileData.objects.filter(
            content_type=content_type, object_id=instance.id
        )

        serializer_context = {"request": request, "volatile_list": list(volatile_items)}
        serializer = self.get_serializer(instance, context=serializer_context)
        return Response(serializer.data)


class CPUViewSet(BaseComponentViewSet):
    queryset = CPU.objects.all().order_by("model")
    serializer_class = CPUSerializer


class GPUViewSet(BaseComponentViewSet):
    queryset = GPU.objects.all().order_by("model")
    serializer_class = GPUSerializer


class MotherboardViewSet(BaseComponentViewSet):
    queryset = Motherboard.objects.all().order_by("model")
    serializer_class = MotherboardSerializer


class RAMViewSet(BaseComponentViewSet):
    queryset = RAM.objects.all().order_by("model")
    serializer_class = RAMSerializer


class StorageViewSet(BaseComponentViewSet):
    queryset = Storage.objects.all().order_by("model")
    serializer_class = StorageSerializer


class PSUViewSet(BaseComponentViewSet):
    queryset = PSU.objects.all().order_by("model")
    serializer_class = PSUSerializer
