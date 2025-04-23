from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.AListHomeProProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('services/', views.ServiceCategoryListView.as_view(), name='service-categories'),
    path('profiles/<int:pk>/', views.AListHomeProProfileDetailView.as_view(), name='alistpro-profile-detail'),
    path('profiles/create/', views.AListHomeProProfileCreateView.as_view(), name='alistpro-profile-create'),
    path('profiles/update/', views.AListHomeProProfileUpdateView.as_view(), name='alistpro-profile-update'),
    path('portfolio/', views.AListHomeProPortfolioListCreateView.as_view(), name='alistpro-portfolio-list-create'),
    path('portfolio/<int:pk>/', views.AListHomeProPortfolioDetailView.as_view(), name='alistpro-portfolio-detail'),
    path('profiles/<int:alistpro_id>/reviews/', views.AListHomeProReviewCreateView.as_view(), name='alistpro-review-create'),
    path('admin/pending/', views.AdminPendingAListHomeProsView.as_view(), name='admin-pending-alistpros'),
]
