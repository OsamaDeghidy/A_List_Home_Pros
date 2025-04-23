from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    AvailabilitySlotViewSet,
    UnavailableDateViewSet,
    AppointmentViewSet,
    AppointmentNoteViewSet
)

# Create a router for main viewsets
router = DefaultRouter()
router.register(r'availability-slots', AvailabilitySlotViewSet, basename='availability-slot')
router.register(r'unavailable-dates', UnavailableDateViewSet, basename='unavailable-date')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

# Create a nested router for appointment notes
appointment_router = routers.NestedDefaultRouter(router, r'appointments', lookup='appointment')
appointment_router.register(r'notes', AppointmentNoteViewSet, basename='appointment-note')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(appointment_router.urls)),
]
