"""alistpros URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI documentation setup
schema_view = get_schema_view(
    openapi.Info(
        title="A-List Home Pros API",
        default_version='v1',
        description="API for A-List Home Pros contractor-client matching platform",
        terms_of_service="https://www.alistpros.com/terms/",
        contact=openapi.Contact(email="contact@alistpros.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include([
        # Auth and user management
        path('users/', include('users.urls')),
        
        # A-List Home Pros management (new name for contractors)
        path('alistpros/', include('alistpros_profiles.urls')),
        
        # Legacy contractor endpoints (kept for backward compatibility)
        path('contractors/', include('contractors.urls')),
        
        # Payment processing
        path('payments/', include('payments.urls')),
        
        # Messaging
        path('messaging/', include('messaging.urls')),
        
        # Scheduling
        path('scheduling/', include('scheduling.urls')),
        
        # Analytics and reporting
        path('analytics/', include('analytics.urls')),
        
        # Notifications
        path('notifications/', include('notifications.urls')),
        
        # Lead management (future)
        # path('leads/', include('leads.urls')),
    ])),
    
    # API documentation
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
