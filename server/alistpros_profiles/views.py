from rest_framework import generics, viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import ServiceCategory, AListHomeProProfile, AListHomeProPortfolio, AListHomeProReview
from .serializers import (
    ServiceCategorySerializer,
    AListHomeProProfileSerializer,
    AListHomeProProfileCreateUpdateSerializer,
    AListHomeProPortfolioSerializer,
    AListHomeProReviewSerializer
)
from .filters import AListHomeProFilter
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


class AListHomeProProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for A-List Home Pro profiles with advanced filtering"""
    queryset = AListHomeProProfile.objects.all()
    serializer_class = AListHomeProProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AListHomeProFilter
    search_fields = ['business_name', 'business_description', 'user__name', 'service_categories__name']
    ordering_fields = ['business_name', 'years_of_experience', 'created_at']
    ordering = ['business_name']


class AListHomeProProfileDetailView(generics.RetrieveAPIView):
    """
    Retrieve an A-List Home Pro profile
    """
    queryset = AListHomeProProfile.objects.all()
    serializer_class = AListHomeProProfileSerializer
    permission_classes = [permissions.AllowAny]


class AListHomeProProfileCreateView(generics.CreateAPIView):
    """
    Create an A-List Home Pro profile (A-List Home Pros only)
    """
    serializer_class = AListHomeProProfileCreateUpdateSerializer
    permission_classes = [IsAListHomePro]
    
    def perform_create(self, serializer):
        # Ensure the profile is linked to the current user
        serializer.save(user=self.request.user)


class AListHomeProProfileUpdateView(generics.UpdateAPIView):
    """
    Update an A-List Home Pro profile (owner only)
    """
    serializer_class = AListHomeProProfileCreateUpdateSerializer
    permission_classes = [IsAListHomePro]
    
    def get_object(self):
        return get_object_or_404(AListHomeProProfile, user=self.request.user)


class AListHomeProPortfolioListCreateView(generics.ListCreateAPIView):
    """
    List and create portfolio items for an A-List Home Pro
    """
    serializer_class = AListHomeProPortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == UserRole.ADMIN:
            return AListHomeProPortfolio.objects.all()
        
        try:
            alistpro_profile = AListHomeProProfile.objects.get(user=self.request.user)
            return AListHomeProPortfolio.objects.filter(alistpro=alistpro_profile)
        except AListHomeProProfile.DoesNotExist:
            return AListHomeProPortfolio.objects.none()
    
    def perform_create(self, serializer):
        alistpro_profile = get_object_or_404(AListHomeProProfile, user=self.request.user)
        serializer.save(alistpro=alistpro_profile)


class AListHomeProPortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a portfolio item
    """
    serializer_class = AListHomeProPortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == UserRole.ADMIN:
            return AListHomeProPortfolio.objects.all()
        
        try:
            alistpro_profile = AListHomeProProfile.objects.get(user=self.request.user)
            return AListHomeProPortfolio.objects.filter(alistpro=alistpro_profile)
        except AListHomeProProfile.DoesNotExist:
            return AListHomeProPortfolio.objects.none()
    
    def check_object_permissions(self, request, obj):
        if request.user.role != UserRole.ADMIN and obj.alistpro.user != request.user:
            self.permission_denied(request, message="You do not have permission to modify this portfolio item.")
        return super().check_object_permissions(request, obj)


class AListHomeProReviewCreateView(generics.CreateAPIView):
    """
    Create a review for an A-List Home Pro (clients only)
    """
    serializer_class = AListHomeProReviewSerializer
    permission_classes = [IsClient]
    
    def perform_create(self, serializer):
        alistpro_id = self.kwargs.get('alistpro_id')
        alistpro_profile = get_object_or_404(AListHomeProProfile, id=alistpro_id)
        
        # Check if the client has already reviewed this A-List Home Pro
        existing_review = AListHomeProReview.objects.filter(
            alistpro=alistpro_profile,
            client=self.request.user
        ).first()
        
        if existing_review:
            raise serializers.ValidationError("You have already reviewed this A-List Home Pro.")
        
        serializer.save(alistpro=alistpro_profile, client=self.request.user)


class AdminPendingAListHomeProsView(generics.ListAPIView):
    """
    List A-List Home Pros that are not yet verified (admin only)
    """
    serializer_class = AListHomeProProfileSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        return AListHomeProProfile.objects.filter(is_onboarded=False)
