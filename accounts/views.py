from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden

from .forms import (
    RegisterForm, LoginForm, ProfileForm,
    TestimonialForm, TopFiveForm, AlbumForm, GalleryImageForm
)
from .models import (
    Profile, FriendRequest, Testimonial, ProfileVisit,
    TopFive, Album, GalleryImage
)


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('accounts:my_profile')
    return redirect('accounts:login')


# Auth views
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Profile created by signal, but ensure it exists
            Profile.objects.get_or_create(user=user)
            messages.success(request, 'Account created. You are logged in.')
            login(request, user)
            return redirect('accounts:my_profile')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        uname_or_email = request.POST.get('username_or_email') or request.POST.get('username')
        pwd = request.POST.get('password')
        username = uname_or_email
        # support login by email
        if '@' in (uname_or_email or ''):
            try:
                u = User.objects.get(email__iexact=uname_or_email)
                username = u.username
            except User.DoesNotExist:
                username = uname_or_email
        user = authenticate(request, username=username, password=pwd)
        if user:
            login(request, user)
            return redirect('accounts:my_profile')
        messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# Dashboard / profile
@login_required
def dashboard(request):
    profile = request.user.profile

    recent_testimonials = profile.testimonials.order_by('-created_at')[:5]

    # Quick friend count: accepted sent + accepted received
    sent_accepted = FriendRequest.objects.filter(
        from_user=request.user, accepted=True
    ).count()
    received_accepted = FriendRequest.objects.filter(
        to_user=request.user, accepted=True
    ).count()
    friends_total = sent_accepted + received_accepted

    # Simple suggestions: show some other users except the current one
    suggestions = User.objects.exclude(id=request.user.id)[:6]

    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'recent_testimonials': recent_testimonials,
        'friends_total': friends_total,
        'suggestions': suggestions,
    })


@login_required
def my_profile(request):
    profile = request.user.profile
    # show visible testimonials to others, but owner sees all - handled in profile view for owner
    testimonials = profile.testimonials.filter(is_hidden=False)
    hidden_testimonials = profile.testimonials.filter(is_hidden=True)
    albums = profile.albums.all()
    gallery_images = profile.gallery.all().order_by('-uploaded_at')[:12]
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'testimonials': testimonials,
        'hidden_testimonials': hidden_testimonials,
        'albums': albums,
        'gallery_images': gallery_images,
    })

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:my_profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile

    # visitor recording
    if request.user.is_authenticated and request.user != user:
        profile.profile_views += 1
        profile.save()
        ProfileVisit.objects.create(profile=profile, visitor=request.user)

    # privacy checks for simplicity: public only or owner
    can_see_profile = (profile.profile_privacy == 'public') or (request.user == user)
    can_see_gallery = (profile.gallery_privacy == 'public') or (request.user == user)
    can_see_testimonials = (profile.testimonial_privacy == 'public') or (request.user == user)

    # testimonials
    if request.user == user:
        testimonials = profile.testimonials.all()
        hidden_testimonials = profile.testimonials.filter(is_hidden=True)
    else:
        testimonials = profile.testimonials.filter(is_hidden=False)
        hidden_testimonials = profile.testimonials.none()

    # mutual friends and interests simple helpers
    def friends_of(u):
        sent = FriendRequest.objects.filter(from_user=u, accepted=True).values_list('to_user', flat=True)
        received = FriendRequest.objects.filter(to_user=u, accepted=True).values_list('from_user', flat=True)
        ids = set(list(sent) + list(received))
        return User.objects.filter(id__in=ids)

    my_friends = friends_of(request.user) if request.user.is_authenticated else User.objects.none()
    owner_friends = friends_of(user)

    mutual_friends = my_friends.filter(id__in=owner_friends.values_list('id', flat=True)) if request.user.is_authenticated else []
    # mutual interests
    def mutual_interests(u1, u2):
        a = set((u1.profile.interests or '').lower().split(',')) if getattr(u1, 'profile', None) else set()
        b = set((u2.profile.interests or '').lower().split(',')) if getattr(u2, 'profile', None) else set()
        a = {s.strip() for s in a if s.strip()}
        b = {s.strip() for s in b if s.strip()}
        return sorted(a & b)

    mutual_interest_list = mutual_interests(request.user, user) if request.user.is_authenticated else []

    return render(request, 'accounts/public_profile.html', {
        'profile': profile,
        'user_obj': user,
        'can_see_profile': can_see_profile,
        'can_see_gallery': can_see_gallery,
        'can_see_testimonials': can_see_testimonials,
        'testimonials': testimonials,
        'hidden_testimonials': hidden_testimonials,
        'mutual_friends': mutual_friends,
        'mutual_interests': mutual_interest_list,
    })


# Friends
@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if to_user == request.user:
        messages.error(request, "You cannot friend yourself.")
        return redirect('accounts:profile', username=to_user.username)
    fr, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    if created:
        messages.success(request, "Friend request sent.")
    else:
        messages.info(request, "Friend request already exists.")
    return redirect('accounts:profile', username=to_user.username)

@login_required
def accept_friend_request(request, req_id):
    fr = get_object_or_404(FriendRequest, id=req_id, to_user=request.user)
    fr.accepted = True
    fr.save()
    messages.success(request, f"You are now friends with {fr.from_user.username}.")
    return redirect('accounts:dashboard')

@login_required
def reject_friend_request(request, req_id):
    fr = get_object_or_404(FriendRequest, id=req_id, to_user=request.user)
    fr.delete()
    messages.info(request, "Friend request rejected.")
    return redirect('accounts:dashboard')


# Testimonials
@login_required
def add_testimonial(request, username):
    owner = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.profile = owner.profile
            t.author = request.user
            t.save()
            messages.success(request, "Posted on their wall.")
            return redirect('accounts:profile', username=owner.username)
    else:
        form = TestimonialForm()
    return render(request, 'accounts/testimonial_form.html', {'form': form, 'profile_user': owner})

@login_required
def hide_testimonial(request, testimonial_id):
    t = get_object_or_404(Testimonial, id=testimonial_id)
    if t.profile.user != request.user:
        return HttpResponseForbidden("Not allowed")
    t.is_hidden = True
    t.save()
    messages.info(request, "Testimonial hidden.")
    return redirect('accounts:my_profile')

@login_required
def unhide_testimonial(request, testimonial_id):
    t = get_object_or_404(Testimonial, id=testimonial_id)
    if t.profile.user != request.user:
        return HttpResponseForbidden("Not allowed")
    t.is_hidden = False
    t.save()
    messages.success(request, "Testimonial is now visible.")
    return redirect('accounts:my_profile')

@login_required
def delete_testimonial(request, testimonial_id):
    t = get_object_or_404(Testimonial, id=testimonial_id)
    if t.profile.user != request.user:
        return HttpResponseForbidden("Not allowed")
    t.delete()
    messages.success(request, "Testimonial deleted.")
    return redirect('accounts:my_profile')


# Visitors
@login_required
def visitor_log(request):
    visits = request.user.profile.visits.select_related('visitor')[:50]
    return render(request, 'accounts/visitor_log.html', {'visits': visits})


# Albums and gallery
@login_required
def album_list(request):
    albums = request.user.profile.albums.all()
    return render(request, 'accounts/album_list.html', {'albums': albums})

@login_required
def album_add(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.profile = request.user.profile
            a.save()
            messages.success(request, "Album created.")
            return redirect('accounts:album_list')
    else:
        form = AlbumForm()
    return render(request, 'accounts/album_form.html', {'form': form})

@login_required
def add_gallery_image(request):
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES)
        form.fields['album'].queryset = request.user.profile.albums.all()
        if form.is_valid():
            gi = form.save(commit=False)
            gi.profile = request.user.profile
            gi.save()
            messages.success(request, "Image added to your gallery.")
            return redirect('accounts:gallery')
    else:
        form = GalleryImageForm()
        form.fields['album'].queryset = request.user.profile.albums.all()
    return render(request, 'accounts/add_gallery_image.html', {'form': form})

@login_required
def gallery(request):
    images = request.user.profile.gallery.all().order_by('-uploaded_at')
    return render(request, 'accounts/gallery.html', {'gallery': images})


# Top five
@login_required
def topfive_list(request):
    tfs = request.user.profile.topfives.all()
    return render(request, 'accounts/topfive_list.html', {'tfs': tfs})

@login_required
def topfive_add(request):
    if request.method == 'POST':
        form = TopFiveForm(request.POST)
        if form.is_valid():
            tf = form.save(commit=False)
            tf.profile = request.user.profile
            tf.save()
            messages.success(request, "Top 5 saved.")
            return redirect('accounts:topfive_list')
    else:
        form = TopFiveForm()
    return render(request, 'accounts/topfive_form.html', {'form': form})

@login_required
def topfive_delete(request, pk):
    tf = get_object_or_404(TopFive, pk=pk, profile=request.user.profile)
    tf.delete()
    messages.info(request, "Top 5 deleted.")
    return redirect('accounts:topfive_list')


# Search
@login_required
def search_users(request):
    q = request.GET.get('q', '')
    results = []
    if q:
        results = User.objects.filter(username__icontains=q) | User.objects.filter(profile__interests__icontains=q)
        results = results.distinct()
    return render(request, 'accounts/search.html', {'query': q, 'results': results})
