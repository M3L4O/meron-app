from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CPUViewSet,
    GPUViewSet,
    MotherboardViewSet,
    PSUViewSet,
    RAMViewSet,
    StorageViewSet,
)

router = DefaultRouter()
router.register(r"cpus", CPUViewSet)
router.register(r"gpus", GPUViewSet)
router.register(r"motherboards", MotherboardViewSet)
router.register(r"rams", RAMViewSet)
router.register(r"psus", PSUViewSet)
router.register(r"storages", StorageViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
