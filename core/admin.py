from django.contrib import admin
from .models import (
    IngredienteBase, 
    ProductoReal, 
    Receta, 
    RecetaIngrediente, 
    PlanSemanal, 
    ComidaPlanificada,
    Supermercado,
    PerfilUsuario
)

# 1. Configuración de INGREDIENTE BASE
@admin.register(IngredienteBase)
class IngredienteBaseAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'calorias', 'dias_caducidad')
    list_filter = ('categoria',)
    search_fields = ('nombre',)

# 2. Configuración de PRODUCTO REAL
@admin.register(ProductoReal)
class ProductoRealAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_comercial', 
        'tipo_unidad',          
        'cantidad_pack',        
        'precio_actual', 
        'precio_por_unidad_medida',
        'peso_gramos'           
    )
    # Quitamos 'nutriscore' si te da guerra, dejamos lo básico
    list_filter = ('supermercado', 'tipo_unidad', 'ingrediente_base__categoria')
    search_fields = ('nombre_comercial', 'ingrediente_base__nombre')

# 3. Configuración de RECETAS
class RecetaIngredienteInline(admin.TabularInline):
    model = RecetaIngrediente
    extra = 1
    autocomplete_fields = ['ingrediente_base']

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    # Quitamos 'calorias_totales' del display si no es un campo guardado, 
    # pero normalmente se calcula. Si da error, lo quitaremos también.
    # Por ahora dejamos lo seguro:
    list_display = ('titulo', 'tiempo_preparacion', 'precio_estimado')
    
    # HE BORRADO 'es_apta_tupper' de aquí abajo 👇
    list_filter = ('es_apta_airfryer', 'es_apta_sarten', 'es_apta_horno') 
    search_fields = ('titulo',)
    inlines = [RecetaIngredienteInline]

# 4. Configuración del PLAN SEMANAL
class ComidaPlanificadaInline(admin.TabularInline):
    model = ComidaPlanificada
    extra = 0
    readonly_fields = ('dia_semana', 'momento', 'receta')
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

@admin.register(PlanSemanal)
class PlanSemanalAdmin(admin.ModelAdmin):
    # HE BORRADO 'creado_en' de aquí abajo 👇
    list_display = ('usuario', 'fecha_inicio') 
    inlines = [ComidaPlanificadaInline]

# 5. Otros registros simples
admin.site.register(Supermercado)
admin.site.register(PerfilUsuario)