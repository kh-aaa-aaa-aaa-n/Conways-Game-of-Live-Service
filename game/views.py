
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required


@login_required
def start_page_view(request):
    return render(request, 'start_page.html')



def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('game:login') 
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# Login view (modify redirect)
def login_view(request):
    if request.user.is_authenticated:
       # If already logged in, redirect to start page
       return redirect('game:start_page') 
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to 'start_page' view name after login
            return redirect('game:start_page') # Use namespaced URL name
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('game:login')

@login_required
def game_view(request):
    # This view now only handles the actual game grid page
    return render(request, 'game.html')

def learn_more(request):
    return render(request, 'learn_more.html')
