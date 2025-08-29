from django.contrib import admin
from .models import Profile, FriendRequest, Testimonial, ProfileVisit, TopFive, Album, GalleryImage

admin.site.register(Profile)
admin.site.register(FriendRequest)
admin.site.register(Testimonial)
admin.site.register(ProfileVisit)
admin.site.register(TopFive)
admin.site.register(Album)
admin.site.register(GalleryImage)
