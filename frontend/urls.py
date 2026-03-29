"""
Frontend URL Configuration
"""
from django.urls import path
from . import views
from .views import ChangePasswordView, DeleteAccountView

app_name = 'frontend'

urlpatterns = [
    # Home
    path('', views.HomeView.as_view(), name='home'),

    # Products
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<int:pk>/', views.CategoryView.as_view(), name='category'),

    # Cart
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.CartAddView.as_view(), name='cart_add'),
    path('cart/update/<int:pk>/', views.CartUpdateView.as_view(), name='cart_update'),
    path('cart/remove/<int:pk>/', views.CartRemoveView.as_view(), name='cart_remove'),

    # Checkout & Orders
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/success/', views.OrderSuccessView.as_view(), name='order_success'),
    path('check-promo/', views.CheckPromoView.as_view(), name='check_promo'),

    # Auth
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Account
    path('account/', views.ProfileView.as_view(), name='profile'),
    path('account/orders/', views.OrdersView.as_view(), name='orders'),
    path('account/orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('account/wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('account/wishlist/add/', views.WishlistAddView.as_view(), name='wishlist_add'),
    path('account/wishlist/remove/<int:pk>/', views.WishlistRemoveView.as_view(), name='wishlist_remove'),
    path('account/location/add/', views.AddLocationView.as_view(), name='add_location'),
    path('account/location/delete/<int:pk>/', views.DeleteLocationView.as_view(), name='delete_location'),
    path('account/password/', ChangePasswordView.as_view(), name='change_password'),
    path('account/delete/', DeleteAccountView.as_view(), name='delete_account'),
]
