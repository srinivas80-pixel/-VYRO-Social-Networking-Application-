from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username or Email',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'})
    )


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}),
        min_length=8
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class ProfileSetupForm(forms.ModelForm):
    display_name = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Display Name'})
    )
    bio = forms.CharField(
        max_length=500, required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Tell us about yourself', 'rows': 3})
    )
    profile_picture = forms.ImageField(required=False)
    location = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Your location'})
    )

    class Meta:
        model = User
        fields = ['display_name', 'bio', 'profile_picture', 'location']


class EditProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    display_name = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Display Name'})
    )
    bio = forms.CharField(
        max_length=500, required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Bio', 'rows': 3})
    )
    location = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Location'})
    )
    website = forms.URLField(
        max_length=200, required=False,
        widget=forms.URLInput(attrs={'placeholder': 'Website'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'})
    )
    profile_picture = forms.ImageField(required=False)
    cover_photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'display_name', 'bio', 'date_of_birth', 'location', 'website', 'profile_picture', 'cover_photo']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This username is already taken.')
        if len(username) < 3:
            raise forms.ValidationError('Username must be at least 3 characters.')
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError('Username can only contain letters, numbers, and underscores.')
        return username


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'email_notifications', 'push_likes', 'push_replies',
            'push_follows', 'push_mentions', 'push_reposts', 'push_messages',
        ]


class PostSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'who_can_reply', 'allow_mentions', 'allow_reposts',
            'allow_comments', 'allow_quote_posts', 'media_visibility',
            'default_post_visibility', 'sensitive_content_warning',
            'show_likes_count', 'show_reposts_count', 'auto_save_drafts',
            'allow_dm_from',
        ]
