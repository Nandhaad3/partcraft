from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
import random
from .models import *

def send_otp_via_email(email):
    try:
        otp = random.randint(100000, 999999)
        subject = 'Your account verification code'
        html_content = render_to_string('myapp/email_templates/welcome_email.html', {'user': user})
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
    #order_id = data['order_id']
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [data['to_email']]

    subject = f'Order Confirmation of the product'
    message = f'Thank you for your order!\n'
    message += f'\n-----------------------------------------------------------------------\n'
    for order_detail in data['order_details']:
        message += (
            f'Order ID: {order_detail["order_id"]}\n'
            f'Product: {order_detail["product_name"]}\n'
            f'Quantity: {order_detail["quantity"]}\n'
            f'Order Date: {order_detail["order_date"]}\n'
            f'Billing Address: {order_detail["billing_address"]}\n'
            f'Shipping Address: {order_detail["shipping_address"]}\n'
        )
    message += f'\n-----------------------------------------------------------------------\n'
    message += f'We will notify you once your order has been shipped.\n'
    message += f'Thank you for shopping with us!\n.'

    send_mail(subject, message, email_from, recipient_list)