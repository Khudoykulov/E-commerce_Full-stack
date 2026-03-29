from celery import shared_task
from django.utils import timezone

from .models import Promo


@shared_task
def set_expire():
    Promo.objects.filter(expire_date__lt=timezone.now()).update(is_expired=True)