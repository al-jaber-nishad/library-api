from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from authentication.models import User
from library.models import Book, Borrow
from library.serializers import (
    BorrowSerializer,
    PenaltyPointsSerializer,
    ReturnBookSerializer,
)
from library.tasks import send_due_date_notification
from utils.throttling import BurstRateThrottle, SustainedRateThrottle


# Borrowing views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([BurstRateThrottle])
def borrow_list(request):
    """List user's borrows or create a new borrow record."""
    if request.method == 'GET':
        # Regular users can see only their borrows, admins can see all
        if request.user.is_staff:
            borrows = Borrow.objects.all()
        else:
            borrows = Borrow.objects.filter(user=request.user)
        
        # Apply filters if provided
        book_id = request.query_params.get('book', None)
        if book_id:
            borrows = borrows.filter(book_id=book_id)
        
        returned = request.query_params.get('returned', None)
        if returned is not None:
            borrows = borrows.filter(returned=(returned.lower() == 'true'))
        
        # Apply ordering if provided
        ordering = request.query_params.get('ordering', '-borrow_date')
        borrows = borrows.order_by(ordering)
        
        serializer = BorrowSerializer(borrows, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Add user to the data before validation
        data = request.data.copy()
        
        # Validate user's borrowing limit (max 3 active borrows)
        active_borrows = Borrow.objects.filter(user=request.user, returned=False).count()
        if active_borrows >= 3:
            return Response(
                {"detail": "You have reached the maximum limit of 3 borrowed books. Please return a book before borrowing another."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check book availability
        book_id = data.get('book')
        if not book_id:
            return Response({"detail": "Book ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if book.available_copies <= 0:
            return Response({"detail": f"Book '{book.title}' is not available for borrowing."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use atomic transaction to ensure consistency
        with transaction.atomic():
            # Decrease available copies
            book.available_copies -= 1
            book.save()
            
            # Create borrow record
            borrow = Borrow(
                user=request.user,
                book=book,
                borrow_date=timezone.now(),
                due_date=timezone.now() + timezone.timedelta(days=14)
            )
            borrow.save()
            
            # Send due date notification
            send_due_date_notification.delay()
            
            serializer = BorrowSerializer(borrow)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SustainedRateThrottle])
def borrow_detail(request, pk):
    """Retrieve a borrow record."""
    try:
        borrow = Borrow.objects.get(pk=pk)
    except Borrow.DoesNotExist:
        return Response({"detail": "Borrow record not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions: only the borrower or admin can view the borrow record
    if borrow.user != request.user and not request.user.is_staff:
        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = BorrowSerializer(borrow)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([BurstRateThrottle])
def return_book(request):
    """Return a borrowed book."""
    serializer = ReturnBookSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        borrow_id = serializer.validated_data['borrow_id']
        
        try:
            borrow = Borrow.objects.get(pk=borrow_id)
        except Borrow.DoesNotExist:
            return Response({"detail": "Borrow record not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions: only the borrower or admin can return the book
        if borrow.user != request.user and not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if already returned
        if borrow.returned:
            return Response({"detail": "This book has already been returned."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use atomic transaction to ensure consistency
        with transaction.atomic():
            # Update the book's available copies
            book = borrow.book
            book.available_copies += 1
            book.save()
            
            # Update the borrow record
            borrow.return_date = timezone.now()
            borrow.returned = True
            borrow.save()
            
            # Calculate and add penalty points if returned late
            penalty_points = borrow.calculate_penalty()
            if penalty_points > 0:
                borrow.user.penalty_points += penalty_points
                borrow.user.save()
            
            response_data = {
                "message": f"Book '{book.title}' returned successfully.",
                "borrow_id": borrow.id,
                "return_date": borrow.return_date,
                "penalty_points_added": penalty_points,
                "total_penalty_points": borrow.user.penalty_points
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SustainedRateThrottle])
def user_penalties(request, user_id=None):
    """View user penalty points."""
    # If user_id is provided, get that user's penalties (admin only)
    # Otherwise, get the current user's penalties
    if user_id and user_id != request.user.id:
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, pk=user_id)
    else:
        user = request.user
    
    serializer = PenaltyPointsSerializer(user)
    return Response(serializer.data)