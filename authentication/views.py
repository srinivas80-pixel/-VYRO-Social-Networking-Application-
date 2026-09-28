from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, ProfileSetupForm

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            from profile_section.models import ContentPreference
            try:
                pref = user.content_preferences
                if not pref.preferences_completed:
                    return redirect('profile_setup')
            except ContentPreference.DoesNotExist:
                return redirect('profile_setup')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'authentication/login.html', {'form': form})


def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile_setup')
    else:
        form = RegisterForm()
    return render(request, 'authentication/register.html', {'form': form})


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                request.session['reset_user_id'] = user.id
                return redirect('reset_password')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'authentication/forgot_password.html', {'form': form})


def reset_password(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('forgot_password')
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(id=user_id)
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                del request.session['reset_user_id']
                messages.success(request, 'Password reset successfully. Please log in.')
                return redirect('login')
            except User.DoesNotExist:
                return redirect('forgot_password')
    else:
        form = ResetPasswordForm()
    return render(request, 'authentication/reset_password.html', {'form': form})


@login_required
def profile_setup(request):
    if request.method == 'POST':
        form = ProfileSetupForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            from profile_section.models import ContentPreference
            pref, _ = ContentPreference.objects.get_or_create(user=request.user)
            interests = request.POST.getlist('interests')
            pref.interests = interests
            pref.preferences_completed = True
            pref.save()
            return redirect('home')
    else:
        form = ProfileSetupForm(instance=request.user)
    return render(request, 'authentication/profile_setup.html', {'form': form})


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('login')
