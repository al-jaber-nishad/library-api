
from django.urls import path
from library.views import category_views as views

urlpatterns = [
    # Author endpoints
    path('category/', views.category_list, name='category-list'),
    path('category/<str:pk>/', views.category_detail, name='category-detail'),
]