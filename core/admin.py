from django.contrib import admin
from .models import Supermercado, IngredienteBase, ProductoReal, Receta, RecetaIngrediente, PerfilUsuario

@admin.register(Supermercado)
class SupermercadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dominio_web')

@admin.register(IngredienteBase)
class IngredienteBaseAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('nombre',)

@admin.register(ProductoReal)
class ProductoRealAdmin(admin.ModelAdmin):
    list_display = ('nombre_comercial', 'supermercado', 'precio_actual', 'precio_por_kg', 'nutriscore')
    list_filter = ('supermercado', 'nutriscore')
    search_fields = ('nombre_comercial',)

class RecetaIngredienteInline(admin.TabularInline):
    model = RecetaIngrediente
    extra = 1

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    inlines = [RecetaIngredienteInline]
    list_display = ('titulo', 'tiempo_preparacion', 'calcular_precio_estimado', 'es_apta_sarten', 'es_apta_airfryer', 'es_apta_horno', 'es_apta_microondas')
    list_filter = ('tiempo_preparacion', 'es_apta_sarten', 'es_apta_airfryer', 'es_apta_horno', 'es_apta_microondas')
    search_fields = ('titulo',)

    def calcular_precio_estimado(self, obj):
        return f"{obj.precio_estimado} €" if obj.precio_estimado else "-"
    calcular_precio_estimado.short_description = "Precio Estimado"

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    # Ahora sí: 'user' coincide con el modelo
    list_display = ('user', 'presupuesto_semanal', 'tiene_airfryer')