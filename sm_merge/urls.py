from django.urls import path, include
from . import views

urlpatterns = [
    path('login', views.LoginView.as_view()),
    path('signup', views.SignupView.as_view()),
    path('verify-otp', views.SignupVerifyOTPView.as_view()),
    path('forgot-password', views.ForgotPasswordRequestView.as_view()),
    path('verify-otp-password', views.ForgotPasswordVerifyOTPView.as_view()),
    path('reset-password', views.ResetPasswordView.as_view()),
    path('auth/google/', views.GoogleLoginView.as_view()),
    path('chat/<str:room_id>/', views.ChatHistoryView.as_view(), name='chat-history'),
]