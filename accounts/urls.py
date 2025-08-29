from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home_redirect, name='home'),

    # auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # dashboard and my profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # public profile
    path('u/<str:username>/', views.profile_view, name='profile'),

    # friends
    path('friend/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend/accept/<int:req_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend/reject/<int:req_id>/', views.reject_friend_request, name='reject_friend_request'),

    # testimonials
    path('testimonial/add/<str:username>/', views.add_testimonial, name='add_testimonial'),
    path('testimonial/hide/<int:testimonial_id>/', views.hide_testimonial, name='hide_testimonial'),
    path('testimonial/unhide/<int:testimonial_id>/', views.unhide_testimonial, name='unhide_testimonial'),
    path('testimonial/delete/<int:testimonial_id>/', views.delete_testimonial, name='delete_testimonial'),

    # visitors
    path('visitors/', views.visitor_log, name='visitor_log'),

    # gallery and albums
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/add/', views.add_gallery_image, name='add_gallery_image'),
    path('albums/', views.album_list, name='album_list'),
    path('albums/add/', views.album_add, name='album_add'),

    # top five
    path('top5/', views.topfive_list, name='topfive_list'),
    path('top5/add/', views.topfive_add, name='topfive_add'),
    path('top5/delete/<int:pk>/', views.topfive_delete, name='topfive_delete'),

    # search
    path('search/', views.search_users, name='search'),
]
