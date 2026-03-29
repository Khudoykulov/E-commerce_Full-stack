"""
Register:
    - /register/ -> send code to user via mail
    - /mail/verify/ -> verify code -> activate, give token

Login:
    - /login/ -> give token

Verify Account:
    - /mail/send/ -> send code to user via mail
    - /mail/verify/ -> verify code -> activate, give token

Change Password:
    - /password/change/ -> change password

Reset Password:
        - /mail/send/ -> send code to user via mail
        - /mail/verify/ -> verify code -> activate, give token
    - /password/reset/ -> reset password
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegisterView,
    LoginView,
    UserLocationUpdateAPIView,
    SuperUserCreateView,
    UserProfileAPIView,
    NewBlockDetailView,
    NewBlockListCreateView,
    AdviceViewSet,
    CallViewSet,
    BannerViewSet,
    CartaViewSet,
    UserDeleteView,
    PasswordChangeView
)

router = DefaultRouter()
router.register(r'location', UserLocationUpdateAPIView, basename='location')
router.register(r'advices', AdviceViewSet, basename='advice')
router.register(r'call', CallViewSet, basename='call')
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'carta', CartaViewSet)  # `/cartas/` API yo‘liga bog‘laymiz

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('profile/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('profile/password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('superuser/create/', SuperUserCreateView.as_view(), name='superuser-create'),
    path('new-blocks/', NewBlockListCreateView.as_view(), name='new-block-list-create'),
    path('new-blocks/<int:pk>/', NewBlockDetailView.as_view(), name='new-block-detail'),
]
