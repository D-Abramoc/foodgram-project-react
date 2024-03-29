from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from recipes.models import ShoppingCart


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    if created:
        ShoppingCart.objects.create(user=instance)
