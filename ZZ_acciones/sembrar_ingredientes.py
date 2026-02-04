import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import IngredienteBase

def sembrar():
    print("🌱 Sembrando Despensa Maestra...")
    
    # Lista Maestra: (Nombre, Categoría)
    # No ponemos macros exactos ahora (0 por defecto), se pueden refinar luego.
    lista = [
        # CARNICERÍA
        ('Pechuga de Pollo', 'Carniceria'), ('Carne Picada Vacuno', 'Carniceria'), 
        ('Lomo de Cerdo', 'Carniceria'), ('Jamón Serrano', 'Carniceria'),
        ('Pavo en Lonchas', 'Carniceria'), ('Salchichas Pollo', 'Carniceria'),

        # PESCADERÍA
        ('Salmón Fresco', 'Pescaderia'), ('Merluza', 'Pescaderia'), 
        ('Atún Lata', 'Pescaderia'), ('Gambas', 'Pescaderia'), ('Bacalao', 'Pescaderia'),

        # FRUTA Y VERDURA
        ('Plátano', 'Fruta'), ('Manzana', 'Fruta'), ('Naranja', 'Fruta'), 
        ('Fresas', 'Fruta'), ('Limón', 'Fruta'), ('Aguacate', 'Verdura'),
        ('Lechuga Iceberg', 'Verdura'), ('Tomate', 'Verdura'), ('Cebolla', 'Verdura'),
        ('Ajo', 'Verdura'), ('Pimiento Rojo', 'Verdura'), ('Pimiento Verde', 'Verdura'),
        ('Calabacín', 'Verdura'), ('Zanahoria', 'Verdura'), ('Espinacas', 'Verdura'),
        ('Patata', 'Verdura'), ('Champiñones', 'Verdura'),

        # LÁCTEOS Y HUEVOS
        ('Leche Entera', 'Lacteos'), ('Leche Semidesnatada', 'Lacteos'), 
        ('Yogur Natural', 'Lacteos'), ('Yogur Griego', 'Lacteos'), ('Queso Batido', 'Lacteos'),
        ('Queso Mozzarella', 'Lacteos'), ('Queso Rallado', 'Lacteos'), ('Mantequilla', 'Lacteos'),
        ('Huevos L', 'Huevos'), ('Claras de Huevo', 'Huevos'),

        # DESPENSA
        ('Arroz Redondo', 'Despensa'), ('Pasta Macarrones', 'Despensa'), ('Espaguetis', 'Despensa'),
        ('Pan de Molde', 'Despensa'), ('Pan Integral', 'Despensa'), ('Avena', 'Despensa'),
        ('Harina de Trigo', 'Despensa'), ('Azúcar', 'Despensa'), ('Sal Fina', 'Despensa'),
        ('Aceite de Oliva', 'Despensa'), ('Aceite de Girasol', 'Despensa'), ('Vinagre', 'Despensa'),
        ('Tomate Frito', 'Despensa'), ('Mayonesa', 'Despensa'),
        ('Café Molido', 'Despensa'), ('Cacao en Polvo', 'Despensa'),
        
        # ESPECIAS (Importante para que no falle al buscar "Orégano")
        ('Orégano', 'Despensa'), ('Pimentón', 'Despensa'), ('Pimienta Negra', 'Despensa'),
        ('Canela', 'Despensa'), ('Comino', 'Despensa')
    ]

    count = 0
    for nombre, cat in lista:
        obj, created = IngredienteBase.objects.get_or_create(
            nombre=nombre,
            defaults={'categoria': cat}
        )
        if created: count += 1

    print(f"✅ {count} nuevos ingredientes añadidos. Total en BD: {IngredienteBase.objects.count()}")

if __name__ == "__main__":
    sembrar()