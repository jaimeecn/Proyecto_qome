import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import Receta, IngredienteBase, RecetaIngrediente

def sembrar_recetas_v2():
    print("🚀 Inyectando Recetas V2 (Compatible Arquitectura Multi-Super)...")

    # 1. Limpieza
    Receta.objects.all().delete()

    # 2. Diccionario Maestro (Simplificado para el ejemplo)
    # Asegúrate de que los nombres coincidan EXACTAMENTE con lo que busca el Scraper
    ingredientes_map = {
        'Pollo': {'cat': 'Carniceria', 'cal': 165},
        'Ternera Picada': {'cat': 'Carniceria', 'cal': 250},
        'Arroz': {'cat': 'Despensa', 'cal': 130},
        'Pasta': {'cat': 'Despensa', 'cal': 131},
        'Tomate Frito': {'cat': 'Despensa', 'cal': 80}, # Ojo al nombre para el scraper
        'Huevos': {'cat': 'Huevos', 'cal': 155},
        'Leche': {'cat': 'Lacteos', 'cal': 42},
        'Aceite Oliva': {'cat': 'Despensa', 'cal': 884},
        'Sal': {'cat': 'Despensa', 'cal': 0},
        'Cebolla': {'cat': 'Verdura', 'cal': 40},
        'Ajo': {'cat': 'Verdura', 'cal': 149},
        'Patata': {'cat': 'Verdura', 'cal': 77},
        'Lechuga': {'cat': 'Verdura', 'cal': 15},
        'Atún Lata': {'cat': 'Despensa', 'cal': 130},
    }

    # Crear Ingredientes Base
    db_ingredientes = {}
    for nombre, datos in ingredientes_map.items():
        ing, _ = IngredienteBase.objects.get_or_create(
            nombre=nombre,
            defaults={'categoria': datos['cat'], 'calorias': datos['cal']}
        )
        db_ingredientes[nombre] = ing

    # 3. Recetario Básico
    recetario = [
        ("Arroz con Pollo", 20, [('Pollo', 150), ('Arroz', 100), ('Aceite Oliva', 10), ('Sal', 2)]),
        ("Pasta Boloñesa", 25, [('Pasta', 100), ('Ternera Picada', 100), ('Tomate Frito', 50), ('Sal', 2)]),
        ("Tortilla de Patatas", 30, [('Huevos', 120), ('Patata', 200), ('Cebolla', 50), ('Aceite Oliva', 20)]),
        ("Ensalada Mixta", 10, [('Lechuga', 150), ('Atún Lata', 60), ('Tomate Frito', 0), ('Aceite Oliva', 10)]), # Tomate frito no pega, pero es para test
        ("Filete con Patatas", 20, [('Pollo', 150), ('Patata', 200), ('Aceite Oliva', 10)]),
    ]

    count = 0
    for nombre, tiempo, ingredientes_lista in recetario:
        # YA NO PASAMOS 'precio_estimado'
        receta = Receta.objects.create(titulo=nombre, tiempo_preparacion=tiempo)
        
        for ing_nom, cantidad in ingredientes_lista:
            base = db_ingredientes.get(ing_nom)
            if not base:
                # Fallback si olvidamos ponerlo en el mapa
                base, _ = IngredienteBase.objects.get_or_create(nombre=ing_nom)
            
            RecetaIngrediente.objects.create(receta=receta, ingrediente_base=base, cantidad_gramos=cantidad)
        
        # Calculamos macros estáticos
        receta.recalcular_macros()
        count += 1

    print(f"\n✅ {count} Recetas inyectadas correctamente.")

if __name__ == "__main__":
    sembrar_recetas_v2()