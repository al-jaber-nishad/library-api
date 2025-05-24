
from django.urls import path
from library.views import author_views as views

urlpatterns = [
    # Author endpoints
    path('authors/', views.author_list, name='author-list'),
    path('authors/<str:pk>/', views.author_detail, name='author-detail'),
]