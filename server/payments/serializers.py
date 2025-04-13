from rest_framework import serializers
from .models import Payment, StripeAccount
from users.serializers import UserSerializer
from contractors.serializers import ContractorProfileSerializer


class StripeAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for Stripe Connect accounts
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = StripeAccount
        fields = (
            'id', 'user', 'stripe_account_id', 'is_details_submitted',
            'is_charges_enabled', 'is_payouts_enabled', 'onboarding_url',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'stripe_account_id', 'is_details_submitted',
            'is_charges_enabled', 'is_payouts_enabled', 'onboarding_url',
            'created_at', 'updated_at'
        )


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for payments
    """
    client = UserSerializer(read_only=True)
    contractor = ContractorProfileSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = (
            'id', 'client', 'contractor', 'amount', 'description',
            'status', 'stripe_payment_intent_id', 'stripe_transfer_id',
            'completed_at', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'client', 'contractor', 'stripe_payment_intent_id',
            'stripe_transfer_id', 'completed_at', 'created_at', 'updated_at'
        )


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating payments
    """
    contractor_id = serializers.IntegerField(write_only=True)
    client_secret = serializers.CharField(read_only=True)
    
    class Meta:
        model = Payment
        fields = ('contractor_id', 'amount', 'description', 'client_secret')
    
    def validate_amount(self, value):
        """
        Validate the payment amount
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value
