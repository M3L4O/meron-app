from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"cpus", views.CPUViewSet, basename="cpu")
router.register(r"gpus", views.GPUViewSet, basename="gpu")
router.register(r"motherboards", views.MotherboardViewSet, basename="motherboard")
router.register(r"rams", views.RAMViewSet, basename="ram")
router.register(r"storages", views.StorageViewSet, basename="storage")
router.register(r"psus", views.PSUViewSet, basename="psu")

urlpatterns = router.urls
