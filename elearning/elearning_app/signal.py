#Create a signal to automatically create or update a Profile when a User is created or updated.
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
# Signal handler to create a user profile when a new User instance is created
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a new Profile instance associated with the newly created User
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Signal handler to save the User's profile whenever the User instance is saved
    instance.profile.save()
