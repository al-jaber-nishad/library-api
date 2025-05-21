from authentication.views import auth as views
from django.urls import path

urlpatterns = [
	path('api/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

	path('api/register/', views.register_user, name='register'),
]