from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceCategoryListView,
    ContractorProfileViewSet,
    ContractorProfileDetailView,
    ContractorProfileCreateView,
    ContractorProfileUpdateView,
    ContractorPortfolioListCreateView,
    ContractorPortfolioDetailView,
    ContractorReviewCreateView,
    AdminPendingContractorsView
)

# Create a router for contractor profiles
router = DefaultRouter()
router.register(r'profiles', ContractorProfileViewSet, basename='contractor-profile')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Service categories
    path('categories/', ServiceCategoryListView.as_view(), name='service-category-list'),
    
    # Legacy contractor profile endpoints
    path('detail/<int:pk>/', ContractorProfileDetailView.as_view(), name='contractor-detail'),
    path('create/', ContractorProfileCreateView.as_view(), name='contractor-create'),
    path('update/', ContractorProfileUpdateView.as_view(), name='contractor-update'),
    
    # Portfolio items
    path('<int:contractor_id>/portfolio/', ContractorPortfolioListCreateView.as_view(), name='portfolio-list-create'),
    path('portfolio/<int:pk>/', ContractorPortfolioDetailView.as_view(), name='portfolio-detail'),
    
    # Reviews
    path('<int:contractor_id>/reviews/', ContractorReviewCreateView.as_view(), name='review-create'),
    
    # Admin endpoints
    path('admin/pending/', AdminPendingContractorsView.as_view(), name='admin-pending-contractors'),
]
