from django.db import models
from django.contrib.auth.models import User

def profile_pic_upload(instance, filename):
    return f"profiles/{instance.user.username}/profile/{filename}"

def cover_upload(instance, filename):
    return f"profiles/{instance.user.username}/cover/{filename}"

def background_upload(instance, filename):
    return f"profiles/{instance.user.username}/background/{filename}"

def gallery_upload(instance, filename):
    return f"gallery/{instance.profile.user.username}/{filename}"

PRIVACY_CHOICES = [
    ("public", "Public"),
    ("friends", "Friends Only"),
    ("private", "Only Me"),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    interests = models.CharField(max_length=255, blank=True, null=True)
    status_message = models.CharField(max_length=120, blank=True, null=True)

    profile_pic = models.ImageField(upload_to=profile_pic_upload, blank=True, null=True)
    cover_photo = models.ImageField(upload_to=cover_upload, blank=True, null=True)
    background_image = models.ImageField(upload_to=background_upload, blank=True, null=True)

    theme_choice = models.CharField(max_length=20, default="default")
    theme_color = models.CharField(max_length=20, default="#ffffff")
    font_choice = models.CharField(max_length=50, default="default")

    music = models.FileField(upload_to="music/", blank=True, null=True)
    music_autoplay = models.BooleanField(default=False)

    profile_views = models.PositiveIntegerField(default=0)

    profile_privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default="public")
    gallery_privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default="public")
    testimonial_privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default="public")

    def __str__(self):
        return self.user.username

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({'accepted' if self.accepted else 'pending'})"

class Testimonial(models.Model):
    profile = models.ForeignKey(Profile, related_name='testimonials', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial to {self.profile.user.username} by {self.author.username}"

class ProfileVisit(models.Model):
    profile = models.ForeignKey(Profile, related_name='visits', on_delete=models.CASCADE)
    visitor = models.ForeignKey(User, on_delete=models.CASCADE)
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visited_at']

    def __str__(self):
        return f"{self.visitor.username} -> {self.profile.user.username} at {self.visited_at}"

class TopFive(models.Model):
    CATEGORIES = [
        ("movies", "Movies"),
        ("music", "Music"),
        ("games", "Games"),
        ("friends", "Friends"),
        ("custom", "Custom"),
    ]
    profile = models.ForeignKey(Profile, related_name='topfives', on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORIES, default='music')
    title = models.CharField(max_length=100, default='My Top 5')
    items = models.TextField(help_text='Enter up to 5 items, one per line')

    created_at = models.DateTimeField(auto_now_add=True)

    def list_items(self):
        return [i.strip() for i in self.items.splitlines() if i.strip()][:5]

    def __str__(self):
        return f"{self.profile.user.username} - {self.title}"

class Album(models.Model):
    profile = models.ForeignKey(Profile, related_name='albums', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.profile.user.username})"

class GalleryImage(models.Model):
    profile = models.ForeignKey(Profile, related_name='gallery', on_delete=models.CASCADE)
    album = models.ForeignKey(Album, related_name='images', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to=gallery_upload)
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image by {self.profile.user.username} ({self.caption})"
