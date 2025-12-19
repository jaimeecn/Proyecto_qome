from django.contrib import admin
from django.urls import path, include
# Añadimos 'perfil' a los imports
from core.views import lista_recetas, detalle_receta, registro, perfil 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', lista_recetas, name='home'),
    path('receta/<int:receta_id>/', detalle_receta, name='detalle_receta'),
    path('registro/', registro, name='registro'),
    path('perfil/', perfil, name='perfil'), # <--- NUEVA RUTA
]