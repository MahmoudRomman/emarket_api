from django.urls import path
from . import views

urlpatterns = [
    
    path('register/', views.user_register, name='user_register'),
    path('request-otp/', views.request_otp, name='request_otp'),
    path('verify-otp/', views.user_login_with_otp, name='verify_otp'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-change/', views.password_change, name='password_change'),
    path('profile/', views.profile, name='profile'),

]
