from rest_framework import generics, viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import ServiceCategory, ContractorProfile, ContractorPortfolio, ContractorReview
from .serializers import (
    ServiceCategorySerializer,
    ContractorProfileSerializer,
    ContractorProfileCreateUpdateSerializer,
    ContractorPortfolioSerializer,
    ContractorReviewSerializer
)
from .filters import ContractorFilter
from users.permissions import IsAListHomePro, IsClient, IsAdmin, IsOwnerOrAdmin
from users.models import UserRole


class ServiceCategoryListView(generics.ListAPIView):
    """
    List all service categories
    """
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class ContractorProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for contractor profiles with advanced filtering"""
    queryset = ContractorProfile.objects.all()
    serializer_class = ContractorProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ContractorFilter
    search_fields = ['business_name', 'description', 'user__name', 'service_categories__name']
    ordering_fields = ['business_name', 'years_in_business', 'created_at']
    ordering = ['business_name']


class ContractorProfileDetailView(generics.RetrieveAPIView):
    """
    Retrieve a contractor profile
    """
    queryset = ContractorProfile.objects.all()
    serializer_class = ContractorProfileSerializer
    permission_classes = [permissions.AllowAny]


class ContractorProfileCreateView(generics.CreateAPIView):
    """
    Create a contractor profile (for contractors only)
    """
    serializer_class = ContractorProfileCreateUpdateSerializer
    permission_classes = [IsAListHomePro]

    def perform_create(self, serializer):
        # Check if user already has a contractor profile
        if hasattr(self.request.user, 'contractor_profile'):
            raise serializers.ValidationError({"detail": "You already have a contractor profile"})
        
        serializer.save(user=self.request.user)


class ContractorProfileUpdateView(generics.UpdateAPIView):
    """
    Update a contractor profile (owner only)
    """
    serializer_class = ContractorProfileCreateUpdateSerializer
    permission_classes = [IsAListHomePro]

    def get_object(self):
        return get_object_or_404(ContractorProfile, user=self.request.user)


class ContractorPortfolioListCreateView(generics.ListCreateAPIView):
    """
    List and create portfolio items for a contractor
    """
    serializer_class = ContractorPortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        contractor_id = self.kwargs.get('contractor_id')
        return ContractorPortfolio.objects.filter(contractor_id=contractor_id)
    
    def perform_create(self, serializer):
        contractor_id = self.kwargs.get('contractor_id')
        contractor = get_object_or_404(ContractorProfile, id=contractor_id)
        
        # Check if the user is the owner of the contractor profile
        if contractor.user != self.request.user and not self.request.user.is_admin:
            raise permissions.PermissionDenied("You don't have permission to add portfolio items to this profile")
        
        serializer.save(contractor=contractor)


class ContractorPortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a portfolio item
    """
    serializer_class = ContractorPortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ContractorPortfolio.objects.all()
    
    def check_object_permissions(self, request, obj):
        # Allow only the contractor who owns this portfolio item or an admin
        if obj.contractor.user != request.user and not request.user.is_admin:
            raise permissions.PermissionDenied("You don't have permission to modify this portfolio item")
        return super().check_object_permissions(request, obj)


class ContractorReviewCreateView(generics.CreateAPIView):
    """
    Create a review for a contractor (clients only)
    """
    serializer_class = ContractorReviewSerializer
    permission_classes = [IsClient]

    def perform_create(self, serializer):
        contractor_id = self.kwargs.get('contractor_id')
        contractor = get_object_or_404(ContractorProfile, id=contractor_id)
        
        # Check if the client has already reviewed this contractor
        if ContractorReview.objects.filter(contractor=contractor, client=self.request.user).exists():
            raise serializers.ValidationError({"detail": "You have already reviewed this contractor"})
        
        serializer.save(contractor=contractor, client=self.request.user)


class AdminPendingContractorsView(generics.ListAPIView):
    """
    List contractors that are not yet verified (admin only)
    """
    serializer_class = ContractorProfileSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return ContractorProfile.objects.filter(user__is_verified=False)
