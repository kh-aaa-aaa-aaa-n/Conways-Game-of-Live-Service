
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os


AVATAR_FILENAMES = [
    'default_avatar.png',
    'avatar1.png',
    'avatar2.png',
    'avatar3.png',
    'avatar4.png'
]


# Create choices tuple for the model field
AVATAR_CHOICES = [(fname, fname.split('.')[0].replace('_', ' ').title()) for fname in AVATAR_FILENAMES]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Avatar Selection
    selected_avatar = models.CharField(
        max_length=100,
        choices=AVATAR_CHOICES,
        default='default_avatar.png', # Ensure this default exists
        blank=False, null=False
    )

    # User Bio
    bio = models.TextField(max_length=250, blank=True, help_text="Tell us a little about yourself (max 250 chars).")

    def __str__(self):
        return f'{self.user.username} Profile'

    # Method to get the static path for the selected avatar
    def get_avatar_url(self):
        from django.templatetags.static import static
        # Construct path relative to the static directory
        return static(os.path.join('images/avatars/', self.selected_avatar))


# Signal receiver to create profile on user creation
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance) 
