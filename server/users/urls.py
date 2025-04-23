from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    UserProfileView,
    PasswordChangeView,
    AdminUserListView,
    AdminUserDetailView,
    CustomTokenObtainPairView,
    VerifyEmailView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', PasswordChangeView.as_view(), name='change_password'),
    
    # Email verification
    path('verify-email/<str:token>/<str:user_id>/', VerifyEmailView.as_view(), name='verify_email'),
    
    # Admin endpoints
    path('admin/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
]
