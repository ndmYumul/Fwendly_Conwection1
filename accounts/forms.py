from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Testimonial, TopFive, Album, GalleryImage

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='Username or Email')
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    THEME_CHOICES = [
        ('default', 'Default'),
        ('dark', 'Dark Mode'),
        ('y2k', 'Y2K Comic Sans'),
    ]
    theme_choice = forms.ChoiceField(choices=THEME_CHOICES, required=False)
    class Meta:
        model = Profile
        fields = [
            'bio', 'location', 'interests', 'status_message',
            'profile_pic', 'cover_photo', 'background_image',
            'theme_choice', 'theme_color', 'font_choice',
            'music', 'music_autoplay',
            'profile_privacy', 'gallery_privacy', 'testimonial_privacy',
        ]

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['content']

class TopFiveForm(forms.ModelForm):
    class Meta:
        model = TopFive
        fields = ['category', 'title', 'items']

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['name']

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['album', 'image', 'caption']
