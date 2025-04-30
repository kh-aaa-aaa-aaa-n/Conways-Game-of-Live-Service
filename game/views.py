from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserUpdateForm, ProfileUpdateForm
# Import Password views and reverse_lazy for redirects
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy
# Import UserProfile model
from .models import UserProfile



@login_required
def start_page_view(request):
    avatar_url = None
    # Check if profile exists before accessing it
    profile = getattr(request.user, 'profile', None)
    if profile:
        avatar_url = profile.get_avatar_url()
    return render(request, 'start_page.html', {'profile_avatar_url': avatar_url})

@login_required
def game_view(request):
    avatar_url = None
    profile = getattr(request.user, 'profile', None)
    if profile:
        avatar_url = profile.get_avatar_url()
    return render(request, 'game.html', {'profile_avatar_url': avatar_url})


# --- Account Management Views ---

@login_required
def account_view(request):
    """Displays the main account page."""
    profile = getattr(request.user, 'profile', None)
    avatar_url = profile.get_avatar_url() if profile else None

    context = {
        'user': request.user,
        'profile': profile, # Pass the profile object or None
        'profile_avatar_url': avatar_url
    }
    return render(request, 'account/account.html', context)

@login_required
def edit_account_view(request):
    """Handles editing user and profile information."""
    profile_instance, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile_instance)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('game:account') # Redirect back to the account page
        else:
             messages.error(request, 'Please correct the errors below.')

    else: # GET request
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile_instance)

    # Get current avatar URL for display in the edit form template
    avatar_url = profile_instance.get_avatar_url()

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'current_avatar_url': avatar_url
    }
    return render(request, 'account/edit_account.html', context)


# --- Password Change Views  ---
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'account/password_change.html' # Your custom template
    success_url = reverse_lazy('game:password_change_done') # Redirect URL name after success

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
     template_name = 'account/password_change_done.html' # Your custom template

# --- Delete Account View ---
@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user_to_delete = request.user # Store user before logout
        logout(request) # Log out first
        user_to_delete.delete() # Delete user (profile cascades)
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('game:login') # Redirect to login page

    # GET request: Show confirmation page
    avatar_url = None
    profile = getattr(request.user, 'profile', None)
    if profile:
        avatar_url = profile.get_avatar_url()

    return render(request, 'account/delete_account_confirm.html', {'profile_avatar_url': avatar_url})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Profile is automatically created by the signal here
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('game:login')
        else:
             messages.error(request, 'Registration failed. Please check the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
       return redirect('game:start_page')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
           
            return redirect('game:start_page')
        else:
             messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('game:login')

def learn_more(request):
    return render(request, 'learn_more.html')
