from django.db import models
from django.contrib.auth.models import User

# 1. Supermercados
class Supermercado(models.Model):
    nombre = models.CharField(max_length=100)
    dominio_web = models.CharField(max_length=100, blank=True)
    color_hex = models.CharField(max_length=7, default="#000000")

    def __str__(self):
        return self.nombre

# 2. Ingredientes Base
class IngredienteBase(models.Model):
    CATEGORIAS = [
        ('Verdura', 'Verdura'), ('Fruta', 'Fruta'), ('Carniceria', 'Carnicería'),
        ('Pescaderia', 'Pescadería'), ('Lacteos', 'Lácteos'), ('Despensa', 'Despensa'),
        ('Panaderia', 'Panadería'), ('Huevos', 'Huevos'), ('Conservas', 'Conservas'),
        ('Otros', 'Otros')
    ]
    nombre = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='Otros')

    def __str__(self):
        return self.nombre

# 3. Productos Reales
class ProductoReal(models.Model):
    ingrediente_base = models.ForeignKey(IngredienteBase, on_delete=models.CASCADE, related_name='productos_disponibles')
    supermercado = models.ForeignKey(Supermercado, on_delete=models.CASCADE)
    nombre_comercial = models.CharField(max_length=200)
    precio_actual = models.DecimalField(max_digits=6, decimal_places=2)
    precio_por_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    peso_gramos = models.IntegerField(default=0)
    imagen_url = models.URLField(max_length=500, blank=True, null=True)
    nutriscore = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_comercial} ({self.precio_actual}€)"

# 4. Recetas
class Receta(models.Model):
    titulo = models.CharField(max_length=200)
    instrucciones = models.TextField()
    tiempo_preparacion = models.IntegerField(help_text="Tiempo en minutos")
    
    # Electrodomésticos
    es_apta_airfryer = models.BooleanField(default=False)
    es_apta_microondas = models.BooleanField(default=False)
    es_apta_horno = models.BooleanField(default=False)
    es_apta_sarten = models.BooleanField(default=False) 
    
    precio_estimado = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.titulo

# 5. Ingredientes de la Receta
class RecetaIngrediente(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name='ingredientes')
    ingrediente_base = models.ForeignKey(IngredienteBase, on_delete=models.CASCADE)
    cantidad_gramos = models.IntegerField()

    def __str__(self):
        return f"{self.ingrediente_base.nombre} ({self.cantidad_gramos}g)"

# 6. Perfil de Usuario
class PerfilUsuario(models.Model):
    # ¡AQUÍ ESTÁ LA CLAVE! Se llama 'user', NO 'usuario'
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    presupuesto_semanal = models.DecimalField(max_digits=6, decimal_places=2, default=50.00)
    tiene_airfryer = models.BooleanField(default=False)
    tiene_microondas = models.BooleanField(default=True)
    tiene_horno = models.BooleanField(default=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"