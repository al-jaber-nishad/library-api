from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('', include('authentication.urls.auth')),
    path('api/', include('library.urls.author_urls')),
    path('api/', include('library.urls.category_urls')),
    path('api/', include('library.urls.book_urls')),
]
