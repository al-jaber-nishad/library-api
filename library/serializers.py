from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from authentication.models import User
from library.models import Author, Category, Book, Borrow


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'author', 'author_name', 
            'category', 'category_name', 'total_copies', 'available_copies',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'available_copies']
    
    def validate(self, data):
        # Ensure available_copies doesn't exceed total_copies
        if 'total_copies' in data and self.instance:
            borrowed = self.instance.total_copies - self.instance.available_copies
            if data['total_copies'] < borrowed:
                raise serializers.ValidationError(
                    f"Total copies cannot be less than currently borrowed books ({borrowed})"
                )
        return data
    
    def create(self, validated_data):
        # Set available_copies equal to total_copies when creating a new book
        validated_data['available_copies'] = validated_data.get('total_copies', 1)
        return super().create(validated_data)

class BorrowSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Borrow
        fields = [
            'id', 'user', 'user_username', 'book', 'book_title',
            'borrow_date', 'due_date', 'return_date', 'returned',
            'days_remaining', 'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'borrow_date', 'due_date', 'return_date', 'returned',
            'created_at', 'updated_at', 'user'
        ]
    
    def get_days_remaining(self, obj):
        if obj.returned:
            return 0
        
        today = timezone.now().date()
        due_date = obj.due_date.date()
        days = (due_date - today).days
        return max(0, days)
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def validate(self, data):
        user = self.context['request'].user
        book = data.get('book')
        
        # Validate book availability
        if book and book.available_copies <= 0:
            raise serializers.ValidationError(f"Book '{book.title}' is not available for borrowing.")
        
        # Check user's active borrows (max 3)
        active_borrows = Borrow.objects.filter(user=user, returned=False).count()
        if active_borrows >= 3:
            raise serializers.ValidationError(
                "You have reached the maximum limit of 3 borrowed books. Please return a book before borrowing another."
            )
        
        return data
    
    def create(self, validated_data):
        # Set the user to the current authenticated user
        validated_data['user'] = self.context['request'].user
        
        # Use atomic transaction to ensure consistency
        with transaction.atomic():
            # Decrease available copies
            book = validated_data['book']
            if book.available_copies <= 0:
                raise serializers.ValidationError("Book is not available for borrowing.")
            
            book.available_copies -= 1
            book.save()
            
            # Create borrow record
            return super().create(validated_data)

class ReturnBookSerializer(serializers.Serializer):
    borrow_id = serializers.CharField()
    
    def validate_borrow_id(self, value):
        user = self.context['request'].user
        
        try:
            borrow = Borrow.objects.get(id=value)
        except Borrow.DoesNotExist:
            raise serializers.ValidationError("Borrow record not found.")
        
        # Only the borrower or admin can return a book
        if borrow.user != user and not user.is_staff:
            raise serializers.ValidationError("You don't have permission to return this book.")
        
        # Check if already returned
        if borrow.returned:
            raise serializers.ValidationError("This book has already been returned.")
        
        return value


class PenaltyPointsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'penalty_points']
        read_only_fields = ['id', 'username', 'penalty_points']