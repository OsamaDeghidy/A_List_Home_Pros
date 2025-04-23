from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.urls import reverse
import stripe
import json
import logging

# Import both models to support backward compatibility during transition
try:
    from alistpros_profiles.models import AListHomeProProfile
    USE_NEW_MODEL = True
except ImportError:
    from contractors.models import ContractorProfile
    USE_NEW_MODEL = False

from .models import Payment, AListHomeProStripeAccount
from .serializers import PaymentSerializer, PaymentCreateSerializer, StripeAccountSerializer
from .utils import (
    create_stripe_account,
    generate_account_link,
    handle_account_updated_webhook,
    create_payment_intent,
    get_stripe_dashboard_link
)
from users.permissions import IsAListHomePro, IsClient, IsAdmin

logger = logging.getLogger(__name__)

# Configure Stripe with the API key
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeOnboardingView(APIView):
    """
    Initiate Stripe Connect onboarding for A-List Home Pros
    """
    permission_classes = [IsAListHomePro]
    
    def post(self, request):
        user = request.user
        
        try:
            # Create or get Stripe account
            stripe_account = create_stripe_account(user)
            
            # Generate account link for onboarding
            base_url = settings.SITE_URL
            refresh_url = f"{base_url}/dashboard/stripe-refresh"
            return_url = f"{base_url}/dashboard/stripe-return"
            
            account_link_url = generate_account_link(
                stripe_account,
                refresh_url,
                return_url
            )
            
            return Response({
                'account_link': account_link_url,
                'stripe_account_id': stripe_account.stripe_account_id,
                'onboarding_started': True
            })
        except Exception as e:
            logger.error(f"Error in StripeOnboardingView: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class StripeAccountStatusView(APIView):
    """
    Check the status of a Stripe Connect account
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            # Get Stripe account
            try:
                stripe_account = AListHomeProStripeAccount.objects.get(user=user)
            except AListHomeProStripeAccount.DoesNotExist:
                return Response({
                    'has_account': False
                })
            
            # Get account information directly from the database
            serializer = StripeAccountSerializer(stripe_account)
            
            # Add additional information
            response_data = serializer.data
            response_data['has_account'] = True
            response_data['onboarding_complete'] = stripe_account.onboarding_complete
            
            # If onboarding is not complete, provide a new link
            if not stripe_account.onboarding_complete:
                base_url = settings.SITE_URL
                refresh_url = f"{base_url}/dashboard/stripe-refresh"
                return_url = f"{base_url}/dashboard/stripe-return"
                
                try:
                    account_link_url = generate_account_link(
                        stripe_account,
                        refresh_url,
                        return_url
                    )
                    response_data['account_link'] = account_link_url
                except Exception as link_error:
                    logger.error(f"Error generating account link: {str(link_error)}")
                    response_data['account_link_error'] = str(link_error)
            
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error in StripeAccountStatusView: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PaymentCreateView(APIView):
    """
    Create a payment from a client to an A-List Home Pro
    """
    permission_classes = [IsClient]
    
    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        pro_id = serializer.validated_data.get('alistpro_id') or serializer.validated_data.get('contractor_id')
        amount = serializer.validated_data['amount']
        description = serializer.validated_data['description']
        
        try:
            # Get A-List Home Pro profile
            if USE_NEW_MODEL:
                pro_profile = get_object_or_404(AListHomeProProfile, id=pro_id)
            else:
                pro_profile = get_object_or_404(ContractorProfile, id=pro_id)
            
            # Create payment intent
            payment_intent = create_payment_intent(
                request.user,
                pro_profile,
                amount,
                description
            )
            
            # Create payment record
            payment_data = {
                'client': request.user,
                'amount': amount,
                'description': description,
                'stripe_payment_intent_id': payment_intent.id
            }
            
            if USE_NEW_MODEL:
                payment_data['alistpro'] = pro_profile
            else:
                payment_data['contractor'] = pro_profile
                
            payment = Payment.objects.create(**payment_data)
            
            return Response({
                'payment_id': payment.id,
                'client_secret': payment_intent.client_secret
            })
        except Exception as e:
            logger.error(f"Error in PaymentCreateView: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PaymentListView(generics.ListAPIView):
    """
    List payments for the authenticated user
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # For clients, show payments they've made
        if user.role == 'client':
            return Payment.objects.filter(client=user).order_by('-created_at')
        
        # For A-List Home Pros, show payments they've received
        elif user.role == 'alistpro' and hasattr(user, 'alistpro_profile'):
            return Payment.objects.filter(alistpro=user.alistpro_profile).order_by('-created_at')
        
        # For admins, show all payments
        elif user.is_admin:
            return Payment.objects.all().order_by('-created_at')
        
        return Payment.objects.none()


class PaymentDetailView(generics.RetrieveAPIView):
    """
    Retrieve a payment
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # For clients, show payments they've made
        if user.role == 'client':
            return Payment.objects.filter(client=user)
        
        # For A-List Home Pros, show payments they've received
        elif user.role == 'alistpro' and hasattr(user, 'alistpro_profile'):
            return Payment.objects.filter(alistpro=user.alistpro_profile)
        
        # For admins, show all payments
        elif user.is_admin:
            return Payment.objects.all()
        
        return Payment.objects.none()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid Stripe webhook payload: {str(e)}")
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid Stripe webhook signature: {str(e)}")
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # Log the event type
    event_type = event['type']
    logger.info(f"Received Stripe webhook: {event_type}")
    
    # Handle the event
    try:
        if event_type == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            payment_id = payment_intent.get('id')
            
            # Find the payment record
            try:
                payment = Payment.objects.get(stripe_payment_intent_id=payment_id)
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.save()
                logger.info(f"Payment {payment_id} marked as completed")
            except Payment.DoesNotExist:
                logger.warning(f"Payment record not found for payment_intent {payment_id}")
                
        elif event_type == 'account.updated':
            handle_account_updated_webhook(event)
            
    except Exception as e:
        logger.error(f"Error processing Stripe webhook {event_type}: {str(e)}")
        # Still return 200 to acknowledge receipt
    
    # Return a response to acknowledge receipt of the event
    return Response({'status': 'success'})


@api_view(['GET'])
@permission_classes([IsAListHomePro])
def stripe_dashboard_link(request):
    """
    Generate a link to the Stripe Express dashboard for an A-List Home Pro
    """
    user = request.user
    
    try:
        # Get Stripe account
        try:
            stripe_account = AListHomeProStripeAccount.objects.get(user=user)
        except AListHomeProStripeAccount.DoesNotExist:
            return Response({
                'error': 'No Stripe account found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate dashboard link using utility function
        dashboard_url = get_stripe_dashboard_link(stripe_account.stripe_account_id)
        
        return Response({
            'url': dashboard_url
        })
    except Exception as e:
        logger.error(f"Error generating Stripe dashboard link: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
