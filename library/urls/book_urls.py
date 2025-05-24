
from django.urls import path
from library.views import book_views as views

urlpatterns = [
    # Book endpoints
    path('book/', views.book_list, name='book-list'),
    path('book/<str:pk>/', views.book_detail, name='book-detail'),
]