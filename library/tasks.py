from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Borrow

@shared_task
def send_due_date_notification(borrow_id):
    """Send email notification for a specific book due date."""
    try:
        borrow = Borrow.objects.get(id=borrow_id)
        
        if not borrow.user.email or borrow.returned:
            return f"Skipped notification for borrow {borrow_id}"
        
        book_title = borrow.book.title
        due_date = borrow.due_date.strftime('%Y-%m-%d')
        
        subject = f'Library Notification: Book Due Today - {book_title}'
        message = f"""
            Hello {borrow.user.username},

            This is a reminder that your borrowed book "{book_title}" is due ({due_date}).

            Please return it within due date to avoid penalty points.

            Thank you,
            Library Management System
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [borrow.user.email],
            fail_silently=False,
        )
        
        return f"Due date notification sent for borrow {borrow_id}"
        
    except Borrow.DoesNotExist:
        return f"Borrow {borrow_id} not found"
    except Exception as e:
        return f"Error sending notification for borrow {borrow_id}: {str(e)}"
