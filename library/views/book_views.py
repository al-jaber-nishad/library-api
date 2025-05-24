from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from library.models import Book
from library.serializers import (
    BookSerializer,
)


@api_view(['GET', 'POST'])
def book_list(request):
    """List all books or create a new book."""
    if request.method == 'GET':
        """List all books or create a new book."""
        books = Book.objects.all()
        # Apply search if provided
        search_query = request.query_params.get('search', None)
        if search_query:
            books = books.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        
        # Apply ordering if provided
        ordering = request.query_params.get('ordering', 'name')
        books = books.order_by(ordering)
        
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        """Create a new book. Admin only."""
        # Check if user is admin
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'DELETE'])
def book_detail(request, pk):
    """Get book details, update or delete an book. Admin only."""
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    """Get book details."""
    if request.method == 'GET':
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookSerializer(book)
        return Response(serializer.data)
    else:
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            """Update or delete an book. Admin only."""
            serializer = BookSerializer(book, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            """Delete an book."""
            book.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)