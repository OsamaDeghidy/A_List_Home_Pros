from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticsDashboardViewSet

router = DefaultRouter()
router.register(r'dashboard', AnalyticsDashboardViewSet, basename='analytics-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
