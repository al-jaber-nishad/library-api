from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from django.db.models import Q

from library.models import Author
from library.serializers import (
    AuthorSerializer,
)
from utils.throttling import SustainedRateThrottle


@api_view(['GET', 'POST'])
@throttle_classes([SustainedRateThrottle])
def author_list(request):
    """List all authors or create a new author."""
    if request.method == 'GET':
        """List all authors or create a new author."""
        authors = Author.objects.all()
        # Apply search if provided
        search_query = request.query_params.get('search', None)
        if search_query:
            authors = authors.filter(Q(name__icontains=search_query) | Q(bio__icontains=search_query))
        
        # Apply ordering if provided
        ordering = request.query_params.get('ordering', 'name')
        authors = authors.order_by(ordering)
        
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        """Create a new author. Admin only."""
        # Check if user is admin
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'DELETE'])
@throttle_classes([SustainedRateThrottle])
def author_detail(request, pk):
    """Get author details, update or delete an author. Admin only."""
    try:
        author = Author.objects.get(pk=pk)
    except Author.DoesNotExist:
        return Response({"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND)

    """Get author details."""
    if request.method == 'GET':
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            return Response({"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AuthorSerializer(author)
        return Response(serializer.data)
    else:
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            """Update or delete an author. Admin only."""
            serializer = AuthorSerializer(author, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            """Delete an author."""
            author.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)