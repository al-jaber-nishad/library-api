
from django.urls import path
from library.views import book_views as views

urlpatterns = [
    # Book endpoints
    path('books/', views.book_list, name='book-list'),
    path('books/<str:pk>/', views.book_detail, name='book-detail'),
]