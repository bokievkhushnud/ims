from celery import shared_task
from django.conf import settings
from datetime import datetime, timedelta
from .models import Item, ItemAssignment
from django.core.mail import EmailMessage

@shared_task
def send_expiry_notification():
    # Get all items with an expiration date that's close
    close_expiry_items = Item.objects.filter(expiration_date__lte=datetime.now() + timedelta(days=7))

    if close_expiry_items.exists():
        # Compose the email message
        subject = 'Item expiry notification'
        message = 'The following items are expiring soon:\n\n'
        for item in close_expiry_items:
            message += f'{item.item_name}: {item.expiration_date}\n'

        # Send the email notification
        email = EmailMessage(subject, message, to=[item.department.head.email])
        email.send()


@shared_task
def send_due_date_notification():
    # Get all items with an expiration date that's close
    close_due_date_items = ItemAssignment.objects.filter(due_date__lte=datetime.now() + timedelta(days=7))

    if close_due_date_items.exists():
        # Compose the email message
        subject = 'Item Due Date'
        message = 'The following items should be returned ASAP:\n\n'
        for item in close_due_date_items:
            message += f'{item.item.item_name}: {item.due_date}\n'
            # Send the email notification
            email = EmailMessage(subject, message, to=[item.item.department.head.email, item.requestor.email])
            email.send()


@shared_task
def send_email_task(subject, message, recipient_list):
    print("Sending")
    email = EmailMessage(subject, message, to=recipient_list)
    email.send()
    print("sent")

