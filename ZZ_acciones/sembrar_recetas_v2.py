import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import Receta, IngredienteBase, RecetaIngrediente

def sembrar_recetas_v2():
    print("🚀 Inyectando Base de Datos de Recetas V2 (BIG DATA)...")

    # 1. Limpieza de Recetas anteriores
    print("🧹 Limpiando recetario antiguo...")
    Receta.objects.all().delete()

    # 2. Definición de Ingredientes Base (Diccionario Maestro)
    ingredientes_map = {
        'Pollo': {'cat': 'Carniceria', 'cal': 165},
        'Ternera Picada': {'cat': 'Carniceria', 'cal': 250},
        'Lomo de Cerdo': {'cat': 'Carniceria', 'cal': 145},
        'Salmón': {'cat': 'Pescaderia', 'cal': 208},
        'Merluza': {'cat': 'Pescaderia', 'cal': 80},
        'Atún Lata': {'cat': 'Despensa', 'cal': 130},
        'Huevos': {'cat': 'Huevos', 'cal': 155},
        'Tofu': {'cat': 'Otros', 'cal': 76},
        'Arroz': {'cat': 'Despensa', 'cal': 130},
        'Pasta': {'cat': 'Despensa', 'cal': 131},
        'Patata': {'cat': 'Verdura', 'cal': 77},
        'Pan Integral': {'cat': 'Despensa', 'cal': 265},
        'Avena': {'cat': 'Despensa', 'cal': 389},
        'Lechuga': {'cat': 'Verdura', 'cal': 15},
        'Tomate': {'cat': 'Verdura', 'cal': 18},
        'Cebolla': {'cat': 'Verdura', 'cal': 40},
        'Zanahoria': {'cat': 'Verdura', 'cal': 41},
        'Brócoli': {'cat': 'Verdura', 'cal': 34},
        'Pimiento': {'cat': 'Verdura', 'cal': 20},
        'Calabacín': {'cat': 'Verdura', 'cal': 17},
        'Espinacas': {'cat': 'Verdura', 'cal': 23},
        'Plátano': {'cat': 'Fruta', 'cal': 89},
        'Manzana': {'cat': 'Fruta', 'cal': 52},
        'Aceite Oliva': {'cat': 'Despensa', 'cal': 884},
        'Yogur Griego': {'cat': 'Lacteos', 'cal': 59},
        'Salsa de Soja': {'cat': 'Despensa', 'cal': 53},
        'Limón': {'cat': 'Fruta', 'cal': 29},
        'Ajo': {'cat': 'Verdura', 'cal': 149},
        'Arroz': {'cat': 'Despensa', 'cal': 130}, # Crudo
        'Arroz Precocinado': {'cat': 'Despensa', 'cal': 130},
    }

    # Asegurar ingredientes en BD
    db_ingredientes = {}
    for nombre, datos in ingredientes_map.items():
        ing, _ = IngredienteBase.objects.get_or_create(nombre=nombre)
        ing.categoria = datos['cat']
        ing.calorias = datos['cal']
        ing.save()
        db_ingredientes[nombre] = ing

    # 3. LISTADO DE RECETAS (20 Variedades)
    recetario = [
        # DESAYUNOS
        ("Porridge de Avena y Plátano", 10, [('Avena', 50), ('Plátano', 100), ('Yogur Griego', 125)]),
        ("Tostadas con Huevo Revuelto", 10, [('Pan Integral', 60), ('Huevos', 120), ('Aceite Oliva', 5)]),
        ("Yogur con Manzana y Avena", 5, [('Yogur Griego', 200), ('Manzana', 150), ('Avena', 30)]),
        
        # COMIDAS/CENAS POLLO
        ("Pollo a la Plancha con Arroz", 20, [('Pollo', 150), ('Arroz', 80), ('Aceite Oliva', 10)]),
        ("Wok de Pollo y Verduras", 25, [('Pollo', 150), ('Pimiento', 50), ('Cebolla', 50), ('Zanahoria', 50), ('Aceite Oliva', 10)]),
        ("Ensalada César con Pollo", 15, [('Lechuga', 200), ('Pollo', 120), ('Pan Integral', 30), ('Yogur Griego', 50)]),
        
        # COMIDAS/CENAS CARNE
        ("Hamburguesa Casera con Patatas", 30, [('Ternera Picada', 150), ('Patata', 200), ('Aceite Oliva', 10)]),
        ("Boloñesa con Pasta", 25, [('Pasta', 80), ('Ternera Picada', 120), ('Tomate', 100), ('Cebolla', 50)]),
        ("Lomo con Pimientos", 15, [('Lomo de Cerdo', 150), ('Pimiento', 100), ('Aceite Oliva', 5)]),

        # COMIDAS/CENAS PESCADO
        ("Salmón al Horno con Patata", 40, [('Salmón', 150), ('Patata', 150), ('Aceite Oliva', 5), ('Limón', 20)]),
        ("Merluza con Verduras", 25, [('Merluza', 180), ('Zanahoria', 50), ('Patata', 100), ('Aceite Oliva', 5)]),
        ("Pasta con Atún y Tomate", 15, [('Pasta', 80), ('Atún Lata', 60), ('Tomate', 100)]),
        ("Ensalada de Arroz y Atún", 15, [('Arroz', 80), ('Atún Lata', 60), ('Tomate', 50), ('Aceite Oliva', 5)]),

        # VEGETARIANO/HUEVOS
        ("Tortilla de Patatas", 30, [('Huevos', 120), ('Patata', 200), ('Cebolla', 50), ('Aceite Oliva', 15)]),
        ("Revuelto de Espinacas", 15, [('Huevos', 120), ('Espinacas', 150), ('Ajo', 5), ('Aceite Oliva', 5)]),
        ("Tofu Salteado con Verduras", 20, [('Tofu', 150), ('Pimiento', 50), ('Calabacín', 50), ('Zanahoria', 50), ('Salsa de Soja', 15)]),
        ("Wok de Tofu y Arroz", 25, [('Tofu', 150), ('Arroz', 80), ('Salsa de Soja', 20), ('Aceite Oliva', 5)]),
        
        # LIGERAS
        ("Crema de Calabacín", 25, [('Calabacín', 200), ('Patata', 50), ('Cebolla', 50), ('Aceite Oliva', 5)]),
        ("Ensalada Mixta Completa", 10, [('Lechuga', 200), ('Tomate', 100), ('Cebolla', 30), ('Atún Lata', 60), ('Huevos', 60)]),
       
       # --- RECETAS "FLASH" (Usan Arroz Precocinado) ---
        ("Arroz Exprés con Atún y Tomate", 5, [('Arroz Precocinado', 125), ('Atún Lata', 60), ('Tomate', 100)]),
        ("Salteado Rápido de Tofu y Arroz", 8, [('Arroz Precocinado', 125), ('Tofu', 150), ('Salsa de Soja', 15)]),
        ("Pollo al Curry Rápido", 10, [('Pollo', 150), ('Arroz Precocinado', 125), ('Yogur Griego', 50)]), # Falso curry con yogur
    ]

    count = 0
    for nombre, tiempo, ingredientes_lista in recetario:
        receta = Receta.objects.create(titulo=nombre, tiempo_preparacion=tiempo, precio_estimado=2.5)
        
        for ing_nom, cantidad in ingredientes_lista:
            # Busca o crea el ingrediente base si no estaba en el mapa (prevención de errores)
            base = db_ingredientes.get(ing_nom)
            if not base:
                base, _ = IngredienteBase.objects.get_or_create(nombre=ing_nom, defaults={'categoria': 'Otros'})
            
            RecetaIngrediente.objects.create(receta=receta, ingrediente_base=base, cantidad_gramos=cantidad)
        count += 1

    print(f"\n✅ {count} Recetas nuevas inyectadas. ¡Adiós a la monotonía!")

if __name__ == "__main__":
    sembrar_recetas_v2()