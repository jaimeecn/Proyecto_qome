from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Receta, PerfilUsuario

# 1. VISTA: LISTA DE RECETAS (Con Buscador y Filtros)
# Asegúrate de que 'PerfilUsuario' esté importado arriba junto a 'Receta'
# from .models import Receta, PerfilUsuario 

def lista_recetas(request):
    recetas = Receta.objects.all()
    perfil = None
    limite_coste = 0 # Valor por defecto

    # 1. INTELIGENCIA DE USUARIO
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfilusuario
            
            # FILTRADO INTELIGENTE (Horno, etc...)
            if not perfil.tiene_horno:
                recetas = recetas.exclude(es_apta_horno=True, es_apta_airfryer=False, es_apta_sarten=False, es_apta_microondas=False)
            if not perfil.tiene_airfryer:
                recetas = recetas.exclude(es_apta_airfryer=True, es_apta_horno=False, es_apta_sarten=False, es_apta_microondas=False)
            if not perfil.tiene_microondas:
                recetas = recetas.exclude(es_apta_microondas=True, es_apta_horno=False, es_apta_sarten=False, es_apta_airfryer=False)

            # --- NUEVO CÁLCULO DE PRESUPUESTO ---
            # Si tu presupuesto son 50€, tienes unos 3.5€ por comida (50 / 14 comidas)
            # Todo lo que supere eso, lo marcaremos en amarillo.
            if perfil.presupuesto_semanal > 0:
                limite_coste = perfil.presupuesto_semanal / 14

        except PerfilUsuario.DoesNotExist:
            pass

    # 2. BÚSQUEDA Y FILTROS MANUALES
    query = request.GET.get('q')
    if query:
        recetas = recetas.filter(titulo__icontains=query)

    if request.GET.get('sarten'): recetas = recetas.filter(es_apta_sarten=True)
    if request.GET.get('airfryer'): recetas = recetas.filter(es_apta_airfryer=True)
    if request.GET.get('microondas'): recetas = recetas.filter(es_apta_microondas=True)
    if request.GET.get('horno'): recetas = recetas.filter(es_apta_horno=True)

    # Enviamos 'limite_coste' al HTML para que pueda comparar fácil
    return render(request, 'core/lista_recetas.html', {
        'recetas': recetas, 
        'perfil': perfil,
        'limite_coste': limite_coste 
    })

# 2. VISTA: DETALLE DE RECETA
def detalle_receta(request, receta_id):
    receta = get_object_or_404(Receta, id=receta_id)
    return render(request, 'core/detalle_receta.html', {'receta': receta})

# 3. VISTA: REGISTRO DE USUARIO
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Logueamos al usuario directamente
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'core/registro.html', {'form': form})

# 4. VISTA: PERFIL DE USUARIO
@login_required
def perfil(request):
    # Buscamos el perfil del usuario actual (o lo creamos si no existe)
    perfil_usuario, created = PerfilUsuario.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Guardamos los datos que vienen del formulario
        perfil_usuario.presupuesto_semanal = request.POST.get('presupuesto')
        
        # Checkboxes: Si no están marcados, no envían nada, así que comprobamos si están en POST
        perfil_usuario.tiene_airfryer = 'airfryer' in request.POST
        perfil_usuario.tiene_horno = 'horno' in request.POST
        perfil_usuario.tiene_microondas = 'microondas' in request.POST
        
        perfil_usuario.save() # Guardamos en la base de datos
        
        return render(request, 'core/perfil.html', {
            'perfil': perfil_usuario, 
            'mensaje': '¡Datos guardados correctamente!'
        })

    return render(request, 'core/perfil.html', {'perfil': perfil_usuario})