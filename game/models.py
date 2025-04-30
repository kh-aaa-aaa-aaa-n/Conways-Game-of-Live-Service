from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
import json


AVATAR_FILENAMES = [
    'default_avatar.png',
    'avatar1.png',
    'avatar2.png',
    'avatar3.png',
    'avatar4.png'
]

AVATAR_CHOICES = [(fname, fname.split('.')[0].replace('_', ' ').title()) for fname in AVATAR_FILENAMES]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Avatar Selection
    selected_avatar = models.CharField(
        max_length=100,
        choices=AVATAR_CHOICES,
        default='default_avatar.png', # default avatar
        blank=False, null=False
    )

    # User Bio
    bio = models.TextField(max_length=250, blank=True, help_text="Tell us a little about yourself (max 250 chars).")

    def __str__(self):
        return f'{self.user.username} Profile'

    # Method to get the static path for the selected avatar
    def get_avatar_url(self):
        from django.templatetags.static import static
        return static(os.path.join('images/avatars/', self.selected_avatar))


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance) # Creates profile with default avatar




class SavedGameState(models.Model):
    """
    Represents a saved state of the Conway's Game of Life grid for a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_game_states')
    name = models.CharField(max_length=100)
  
    grid_state_json = models.TextField(help_text="Stores the grid state as a JSON string (e.g., list of live cell coordinates)")
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        # Ensure a user cannot have two saves with the same name
        unique_together = ('user', 'name')
        ordering = ['-timestamp'] # Show newest saves first

    def __str__(self):
        return f"'{self.name}' saved by {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def set_grid_state(self, grid_data):
        """Serializes grid data (e.g., list of lists or list of coords) into JSON."""
        self.grid_state_json = json.dumps(grid_data)

    def get_grid_state(self):
        """Deserializes JSON string back into Python object."""
        try:
            return json.loads(self.grid_state_json)
        except json.JSONDecodeError:
            return None # Or return an empty grid representation
