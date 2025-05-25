
from django.urls import path
from library.views import borrow_views as views

urlpatterns = [
    # Borrowing endpoints
    path('borrow/', views.borrow_list, name='borrow-list'),
    path('borrow/<int:pk>/', views.borrow_detail, name='borrow-detail'),
    path('return/', views.return_book, name='return-book'),
    path('users/<int:user_id>/penalties/', views.user_penalties, name='user-penalties'),
    
]
