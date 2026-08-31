from .models import Profile

ZOOM_OPTIONS = (70, 85, 100, 120, 140)


def profile_settings(request):
    zoom = 100
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        zoom = profile.zoom_level
    return {'zoom_level': zoom, 'zoom_options': ZOOM_OPTIONS}
