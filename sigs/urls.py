from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs de autenticación
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    
    # URLs de la app core (incluye logout y gestión de niños)
    path('', include('core.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)