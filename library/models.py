from django.db import models
from authentication.models import User
from django.utils import timezone
from datetime import timedelta
from utils.mixins import BaseModel

# Create your models here.
class Author(BaseModel):
    """Model to store author information."""
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Category(BaseModel):
    """Model to store book categories."""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']


class Book(BaseModel):
    """Model to store book information."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']
    
    def is_available(self):
        """Check if the book has available copies."""
        return self.available_copies > 0


class Borrow(BaseModel):
    """Model to store borrowing records."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrows')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrows')
    borrow_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    returned = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
    
    def save(self, *args, **kwargs):
        # Set due date if not already set
        if not self.due_date:
            self.due_date = self.borrow_date + timedelta(days=14)
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        """Check if the book is overdue."""
        if self.returned:
            return self.return_date > self.due_date
        return timezone.now() > self.due_date
    
    def calculate_penalty(self):
        """Calculate penalty points for late return."""
        if not self.returned:
            return 0
        
        if self.return_date <= self.due_date:
            return 0
        
        # Calculate days late
        days_late = (self.return_date - self.due_date).days
        return max(0, days_late)  # 1 point per day late
    
    class Meta:
        ordering = ['-borrow_date']