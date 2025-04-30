# convoy_game/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static # Keep import if serving static files this way

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('game.urls')), # Include your app's URLs (ensure this matches your app's urls.py)
]

# --- Serve Static files during development ---
# This block helps the development server find your static files.
if settings.DEBUG:
    # Check if STATICFILES_DIRS is defined and not empty
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # --- Media URL Pattern (Removed) ---
    # if settings.MEDIA_ROOT:
    #     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # --- End of Media URL Pattern Removal ---

# Note: For production, you should configure your web server (like Nginx or Apache)
# to serve static and media files directly. The static() helper is not suitable for production.