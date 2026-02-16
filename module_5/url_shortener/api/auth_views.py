from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .auth_serializers import UserRegistrationSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    """
    Custom Login view with rate limiting.
    """

    throttle_scope = "login"
    permission_classes = [AllowAny]
