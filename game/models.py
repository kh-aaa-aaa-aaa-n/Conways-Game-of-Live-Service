from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
import json


# ==== Avatar + UserProfile ====
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
    selected_avatar = models.CharField(
        max_length=100,
        choices=AVATAR_CHOICES,
        default='default_avatar.png',
        blank=False, null=False
    )
    bio = models.TextField(max_length=250, blank=True, help_text="Tell us a little about yourself (max 250 chars).")

    def __str__(self):
        return f'{self.user.username} Profile'

    def get_avatar_url(self):
        from django.templatetags.static import static
        return static(os.path.join('images/avatars/', self.selected_avatar))


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# ==== Saved Game State ====
class SavedGameState(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_game_states')
    name = models.CharField(max_length=100)
    grid_state_json = models.TextField(help_text="Stores the grid state as a JSON string (e.g., list of live cell coordinates)")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['-timestamp']

    def __str__(self):
        return f"'{self.name}' saved by {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def set_grid_state(self, grid_data):
        self.grid_state_json = json.dumps(grid_data)

    def get_grid_state(self):
        try:
            return json.loads(self.grid_state_json)
        except json.JSONDecodeError:
            return None


# ==== NEW: Game Action Logging Model ====
class GameAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    turn = models.IntegerField()
    action = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Turn {self.turn}: {self.action} — {self.result}"
