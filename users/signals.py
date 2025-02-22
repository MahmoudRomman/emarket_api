from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models

@receiver(post_save, sender=models.CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a profile for a user when they are registered.
    """
    if created:  # Only create a profile if the user is newly created
        models.Profile.objects.create(user=instance)

@receiver(post_save, sender=models.CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the profile whenever the user is saved.
    """
    instance.profile.save()