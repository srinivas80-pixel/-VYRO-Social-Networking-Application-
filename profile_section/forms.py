from django import forms
from .models import ContentPreference


class ContentPreferenceForm(forms.ModelForm):
    INTEREST_CHOICES = [
        ('technology', 'Technology'),
        ('sports', 'Sports'),
        ('music', 'Music'),
        ('gaming', 'Gaming'),
        ('news', 'News'),
        ('entertainment', 'Entertainment'),
        ('science', 'Science'),
        ('politics', 'Politics'),
        ('fashion', 'Fashion'),
        ('art', 'Art'),
        ('food', 'Food'),
        ('travel', 'Travel'),
        ('fitness', 'Fitness'),
        ('photography', 'Photography'),
        ('business', 'Business'),
    ]

    interests = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'interest-checkbox'}),
        required=False
    )

    class Meta:
        model = ContentPreference
        fields = ['interests']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.preferences_completed = True
        if commit:
            instance.save()
        return instance
