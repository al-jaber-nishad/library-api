from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from utils.throttling import SustainedRateThrottle
from rest_framework.response import Response
from library.models import Category
from library.serializers import (
    CategorySerializer,
)


@api_view(['GET', 'POST'])
@throttle_classes([SustainedRateThrottle])
def category_list(request):
    """List all categorys or create a new category."""
    if request.method == 'GET':
        """List all categorys or create a new category."""
        categorys = Category.objects.all()
        # Apply search if provided
        search_query = request.query_params.get('search', None)
        if search_query:
            categorys = categorys.filter(name__icontains=search_query)
        
        # Apply ordering if provided
        ordering = request.query_params.get('ordering', 'name')
        categorys = categorys.order_by(ordering)
        
        serializer = CategorySerializer(categorys, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        """Create a new category. Admin only."""
        # Check if user is admin
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, pk):
    """Get category details, update or delete an category. Admin only."""
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    """Get category details."""
    if request.method == 'GET':
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    else:
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            """Update or delete an category. Admin only."""
            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            """Delete an category."""
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)