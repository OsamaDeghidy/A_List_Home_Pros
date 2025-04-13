from rest_framework import serializers
from .models import ServiceCategory, AListHomeProProfile, AListHomeProPortfolio, AListHomeProReview
from users.serializers import UserSerializer


class ServiceCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for service categories
    """
    class Meta:
        model = ServiceCategory
        fields = ('id', 'name', 'description', 'created_at')


class AListHomeProPortfolioSerializer(serializers.ModelSerializer):
    """
    Serializer for A-List Home Pro portfolio items
    """
    class Meta:
        model = AListHomeProPortfolio
        fields = ('id', 'title', 'description', 'image', 'completion_date', 'created_at')
        read_only_fields = ('created_at',)


class AListHomeProReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for A-List Home Pro reviews
    """
    client_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AListHomeProReview
        fields = ('id', 'client', 'client_name', 'rating', 'comment', 'is_verified', 'created_at')
        read_only_fields = ('client', 'is_verified', 'created_at')
    
    def get_client_name(self, obj):
        return obj.client.name


class AListHomeProProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for A-List Home Pro profiles
    """
    user = UserSerializer(read_only=True)
    service_categories = ServiceCategorySerializer(many=True, read_only=True)
    portfolio_items = AListHomeProPortfolioSerializer(many=True, read_only=True)
    reviews = AListHomeProReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = AListHomeProProfile
        fields = (
            'id', 'user', 'business_name', 'business_description',
            'years_of_experience', 'license_number', 'insurance_info',
            'service_radius', 'profile_image', 'is_onboarded',
            'service_categories', 'portfolio_items', 'reviews',
            'average_rating', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return 0
        total = sum(review.rating for review in reviews)
        return round(total / len(reviews), 1)


class AListHomeProProfileCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating A-List Home Pro profiles
    """
    service_category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = AListHomeProProfile
        fields = (
            'business_name', 'business_description', 
            'years_of_experience', 'license_number', 'insurance_info',
            'service_radius', 'profile_image', 'service_category_ids'
        )
    
    def create(self, validated_data):
        service_category_ids = validated_data.pop('service_category_ids', [])
        
        # Get the current user from the context
        user = self.context['request'].user
        
        # Create the profile
        profile = AListHomeProProfile.objects.create(
            user=user,
            **validated_data
        )
        
        # Add service categories
        if service_category_ids:
            categories = ServiceCategory.objects.filter(id__in=service_category_ids)
            profile.service_categories.set(categories)
        
        return profile
    
    def update(self, instance, validated_data):
        service_category_ids = validated_data.pop('service_category_ids', None)
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update service categories if provided
        if service_category_ids is not None:
            categories = ServiceCategory.objects.filter(id__in=service_category_ids)
            instance.service_categories.set(categories)
        
        return instance
