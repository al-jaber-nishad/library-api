from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from utils.throttling import AuthenticationRateThrottle
from authentication.serializers import UserSerializer

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            # Serialize user data and add it to the response
            serializer_data = UserSerializer(self.user).data
            data.update(serializer_data)

            # Add user_id to the response
            data['user_id'] = self.user.id
            return data

        except PermissionDenied as e:
            # Catch PermissionDenied and return a custom response
            raise ValidationError({'detail': str(e)}, code=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # Handle any other exceptions
            raise ValidationError({'detail': str(e)}, code=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    """API endpoint for login."""
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthenticationRateThrottle])
def register_user(request):
    """API endpoint for user registration."""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
