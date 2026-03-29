# import os
# from django.core.mail import send_mail
# from config.celery import app
#
#
# @app.task(bind=True)
# def ecommerce_send_email(self, subject, message, recipient_list, *args, **kwargs):
#     from_email = os.getenv('EMAIL_HOST_USER')
#     send_mail(subject, message, from_email, recipient_list)
#
