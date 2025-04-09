from rest_framework import serializers
from .models import ServiceCategory, ContractorProfile, ContractorPortfolio, ContractorReview
from users.serializers import UserSerializer


class ServiceCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for service categories
    """
    class Meta:
        model = ServiceCategory
        fields = ('id', 'name', 'description', 'created_at')


class ContractorPortfolioSerializer(serializers.ModelSerializer):
    """
    Serializer for contractor portfolio items
    """
    class Meta:
        model = ContractorPortfolio
        fields = ('id', 'title', 'description', 'image', 'completion_date', 'created_at')
        read_only_fields = ('created_at',)


class ContractorReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for contractor reviews
    """
    client_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ContractorReview
        fields = ('id', 'client', 'client_name', 'rating', 'comment', 'is_verified', 'created_at')
        read_only_fields = ('client', 'is_verified', 'created_at')
    
    def get_client_name(self, obj):
        return obj.client.name


class ContractorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for contractor profiles
    """
    user = UserSerializer(read_only=True)
    service_categories = ServiceCategorySerializer(many=True, read_only=True)
    portfolio_items = ContractorPortfolioSerializer(many=True, read_only=True)
    reviews = ContractorReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = ContractorProfile
        fields = (
            'id', 'user', 'business_name', 'business_description', 
            'years_of_experience', 'license_number', 'insurance_info',
            'service_radius', 'profile_image', 'is_onboarded',
            'service_categories', 'portfolio_items', 'reviews',
            'average_rating', 'created_at', 'updated_at'
        )
        read_only_fields = ('user', 'is_onboarded', 'created_at', 'updated_at')
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)


class ContractorProfileCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating contractor profiles
    """
    service_category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ContractorProfile
        fields = (
            'business_name', 'business_description', 
            'years_of_experience', 'license_number', 'insurance_info',
            'service_radius', 'profile_image', 'service_category_ids'
        )
    
    def create(self, validated_data):
        service_category_ids = validated_data.pop('service_category_ids', [])
        
        # Create the contractor profile
        contractor_profile = ContractorProfile.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
        
        # Add service categories
        if service_category_ids:
            service_categories = ServiceCategory.objects.filter(id__in=service_category_ids)
            contractor_profile.service_categories.add(*service_categories)
        
        return contractor_profile
    
    def update(self, instance, validated_data):
        service_category_ids = validated_data.pop('service_category_ids', None)
        
        # Update the contractor profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update service categories if provided
        if service_category_ids is not None:
            service_categories = ServiceCategory.objects.filter(id__in=service_category_ids)
            instance.service_categories.clear()
            instance.service_categories.add(*service_categories)
        
        return instance
