# game/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, AVATAR_CHOICES # Import choices

# Form to update core User fields (username, email, etc.)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

# Form to update Profile fields (avatar, bio)
class ProfileUpdateForm(forms.ModelForm):
    # Avatar selection using Radio buttons
    selected_avatar = forms.ChoiceField(
        choices=AVATAR_CHOICES,
        widget=forms.RadioSelect, # Use RadioSelect widget
        required=True,
        label="Choose Your Avatar"
    )

    # Bio Field using Textarea
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your bio...'}),
        max_length=250,
        required=False,
        help_text="Max 250 characters."
    )

    class Meta:
        model = UserProfile
        # Only include these fields from UserProfile
        fields = ['selected_avatar', 'bio']