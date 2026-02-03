import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import Receta, IngredienteBase, RecetaIngrediente

def sembrar_recetas_v3():
    print("🚀 Inyectando Recetas V3 (Maximizando Ingredientes Existentes)...")

    # 1. Limpieza
    Receta.objects.all().delete()

    # 2. Recuperar Ingredientes (Ya deben existir del paso anterior)
    def get_ing(nombre):
        try:
            return IngredienteBase.objects.get(nombre__icontains=nombre)
        except IngredienteBase.DoesNotExist:
            # Fallback de emergencia por si algo falta
            print(f"⚠️ Creando ingrediente faltante: {nombre}")
            return IngredienteBase.objects.create(nombre=nombre, categoria='Otros')
        except IngredienteBase.MultipleObjectsReturned:
            return IngredienteBase.objects.filter(nombre__icontains=nombre).first()

    # Lista de ingredientes que SABEMOS que tienes:
    # Pollo, Ternera, Arroz, Pasta, Tomate, Huevos, Leche, Aceite, Sal, Cebolla, Ajo, Patata, Lechuga, Atún

    recetario = [
        # --- CLÁSICOS (5) ---
        ("Arroz con Pollo", 20, [('Pollo', 150), ('Arroz', 100), ('Aceite Oliva', 10), ('Sal', 2), ('Ajo', 5)]),
        ("Pasta Boloñesa", 25, [('Pasta', 100), ('Ternera Picada', 100), ('Tomate Frito', 50), ('Sal', 2), ('Cebolla', 30)]),
        ("Tortilla de Patatas", 30, [('Huevos', 120), ('Patata', 200), ('Cebolla', 50), ('Aceite Oliva', 20), ('Sal', 2)]),
        ("Ensalada Mixta", 10, [('Lechuga', 150), ('Atún Lata', 60), ('Tomate Frito', 20), ('Aceite Oliva', 10), ('Sal', 1)]), # Tomate frito a falta de natural
        ("Filete con Patatas", 20, [('Pollo', 150), ('Patata', 200), ('Aceite Oliva', 10), ('Sal', 2)]),

        # --- NUEVAS COMBINACIONES (9) ---
        ("Arroz a la Cubana", 15, [('Arroz', 100), ('Huevos', 60), ('Tomate Frito', 60), ('Aceite Oliva', 10), ('Sal', 2)]),
        ("Macarrones con Atún", 15, [('Pasta', 100), ('Atún Lata', 60), ('Tomate Frito', 60), ('Cebolla', 20)]),
        ("Pollo al Ajillo", 25, [('Pollo', 200), ('Ajo', 15), ('Patata', 150), ('Aceite Oliva', 15), ('Sal', 2)]),
        ("Revuelto de Atún", 10, [('Huevos', 120), ('Atún Lata', 60), ('Cebolla', 40), ('Aceite Oliva', 5), ('Sal', 1)]),
        ("Ensalada de Pasta", 15, [('Pasta', 80), ('Atún Lata', 60), ('Lechuga', 50), ('Aceite Oliva', 10), ('Sal', 1)]),
        ("Hamburguesa Casera con Puré", 25, [('Ternera Picada', 150), ('Patata', 150), ('Leche', 20), ('Ajo', 2), ('Sal', 2)]),
        ("Tortilla Francesa y Ensalada", 10, [('Huevos', 120), ('Lechuga', 100), ('Aceite Oliva', 10), ('Sal', 1)]),
        ("Pastel de Carne y Patata", 40, [('Ternera Picada', 150), ('Patata', 200), ('Leche', 20), ('Tomate Frito', 30), ('Queso', 0)]), # Sin queso por ahora
        ("Salteado de Pollo y Arroz", 20, [('Pollo', 100), ('Arroz', 100), ('Cebolla', 50), ('Ajo', 5), ('Aceite Oliva', 10)]),
    ]

    count = 0
    for nombre, tiempo, ingredientes_lista in recetario:
        receta = Receta.objects.create(titulo=nombre, tiempo_preparacion=tiempo)
        
        for ing_nom, cantidad in ingredientes_lista:
            if cantidad == 0: continue # Saltamos ingredientes fantasma
            
            base = get_ing(ing_nom)
            RecetaIngrediente.objects.create(receta=receta, ingrediente_base=base, cantidad_gramos=cantidad)
        
        receta.recalcular_macros()
        count += 1

    print(f"\n✅ {count} Recetas inyectadas (Usando despensa existente).")

if __name__ == "__main__":
    sembrar_recetas_v3()