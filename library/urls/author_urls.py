
from django.urls import path
from library.views import author_views as views

urlpatterns = [
    # Author endpoints
    path('authors/', views.author_list, name='author-list'),
    path('authors/<int:pk>/', views.author_detail_get, name='author-detail'),
    path('authors/<int:pk>/', views.author_detail_admin, name='author-detail-admin'),
    
]