from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CPUViewSet,
    GPUViewSet,
    MotherboardViewSet,
    RAMViewSet,
    StorageViewSet,
    PSUViewSet,
    VolatileViewSet,
)

router = DefaultRouter()
router.register(r"cpus", CPUViewSet)
router.register(r"gpus", GPUViewSet)
router.register(r"motherboards", MotherboardViewSet)
router.register(r"rams", RAMViewSet)
router.register(r"storages", StorageViewSet)
router.register(r"psus", PSUViewSet)
router.register(r"volatiles", VolatileViewSet, basename="volatile")
urlpatterns = [
    path("", include(router.urls)),
]
