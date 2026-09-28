from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    content = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'placeholder': "What's happening?",
            'rows': 3,
            'maxlength': '500'
        })
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    video = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'video/*'})
    )

    class Meta:
        model = Post
        fields = ['content', 'image', 'video']

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content', '').strip()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        if not content and not image and not video:
            raise forms.ValidationError('Post must have text, an image, or a video.')
        return cleaned_data
