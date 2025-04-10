# convoy_game/urls.py
from django.contrib import admin
from django.urls import path, include  # Ensure 'include' is imported
from django.conf import settings       # Ensure 'settings' is imported
from django.conf.urls.static import static  # Ensure 'static' is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', include('game.urls')),
]

# --- This block MUST be present and correct ---
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
# --- End of block ---