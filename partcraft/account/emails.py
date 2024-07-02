from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, EmailMessage
import random
from .models import *

def send_otp_via_email(email):
    try:
        otp = random.randint(100000, 999999)
        subject = 'Your account verification code'
        message = f'Your OTP for email verification: {otp}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
        user_obj, created = User.objects.get_or_create(email=email)
        user_obj.otp = otp
        user_obj.save()
        return True, "OTP sent successfully"
    except ObjectDoesNotExist:
        return False, "User not found"
    except Exception as e:
        return False, str(e)

class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email=settings.EMAIL_HOST_USER,
            to=[data['to_email']],
        )
        email.send()

def send_confirmation_email(data):
    from parts.models import Order
    order_id = data['order_id']
    subject = f'Order Confirmation of the product #{Order.order_id}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [data['to_email']]

    order = Order.objects.get(id=order_id)
    message = (
        f'Thank you for your order!\n'
        f'Order ID: {order.order_id}\n'
        f'Product: {order.product}\n'
        f'Quantity: {order.quantity}\n'
        f'Order Date: {order.order_date}\n'
        f'Billing Address: {order.billing_address}\n'
        f'Shipping Address: {order.shipping_address}\n'
        'We will notify you once your order has been shipped.\n'
        'Thank you for shopping with us!\n'
    )

    send_mail(subject, message, email_from, recipient_list)
