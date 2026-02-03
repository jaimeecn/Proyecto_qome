import os
import django
import sys

# Ajusta esto para que encuentre tu proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import IngredienteBase

def sembrar_nutricion():
    print("🥗 Sembrando datos nutricionales (Base de Datos Maestra)...")

    # DICCIONARIO MAESTRO (Datos aproximados por 100g)
    # Valores estándar de mercado (USDA / BEDCA)
    datos_nutricionales = {
        # --- CARNES Y PESCADOS ---
        'Pollo': {'cal': 165, 'prot': 31, 'gras': 3.6, 'hid': 0},
        'Pechuga': {'cal': 110, 'prot': 23, 'gras': 1.2, 'hid': 0},
        'Ternera': {'cal': 250, 'prot': 26, 'gras': 15, 'hid': 0},
        'Cerdo': {'cal': 145, 'prot': 21, 'gras': 6, 'hid': 0},
        'Salmón': {'cal': 208, 'prot': 20, 'gras': 13, 'hid': 0},
        'Atún': {'cal': 130, 'prot': 28, 'gras': 1, 'hid': 0},
        'Merluza': {'cal': 80, 'prot': 17, 'gras': 1, 'hid': 0},
        
        # --- PROTEÍNA VEGETAL ---
        'Tofu': {'cal': 120, 'prot': 12, 'gras': 7, 'hid': 2}, # Tofu firme promedio
        'Garbanzos': {'cal': 95, 'prot': 5.5, 'gras': 1.5, 'hid': 13}, # Bote/Cocido (¡Ojo! No en seco)
        'Lentejas': {'cal': 90, 'prot': 6, 'gras': 0.4, 'hid': 15}, # Bote/Cocido
        'Quinoa': {'cal': 368, 'prot': 14, 'gras': 6, 'hid': 64}, # Cruda
        
        # --- VERDURAS Y HORTALIZAS ---
        'Brócoli': {'cal': 34, 'prot': 2.8, 'gras': 0.4, 'hid': 7},
        'Espinacas': {'cal': 23, 'prot': 2.9, 'gras': 0.4, 'hid': 3.6},
        'Zanahoria': {'cal': 41, 'prot': 0.9, 'gras': 0.2, 'hid': 10},
        'Cebolla': {'cal': 40, 'prot': 1.1, 'gras': 0.1, 'hid': 9},
        'Pimiento': {'cal': 20, 'prot': 0.9, 'gras': 0.2, 'hid': 4.6},
        'Calabacín': {'cal': 17, 'prot': 1.2, 'gras': 0.3, 'hid': 3},
        'Tomate Frito': {'cal': 70, 'prot': 1.5, 'gras': 3.5, 'hid': 9}, # Específico procesado
        'Tomate': {'cal': 18, 'prot': 0.9, 'gras': 0.2, 'hid': 3.9}, # Genérico fresco
        'Lechuga': {'cal': 15, 'prot': 1.4, 'gras': 0.2, 'hid': 2.9},
        'Champiñones': {'cal': 22, 'prot': 3.1, 'gras': 0.3, 'hid': 3.3},
        'Ajo': {'cal': 149, 'prot': 6.4, 'gras': 0.5, 'hid': 33},
        'Aguacate': {'cal': 160, 'prot': 2, 'gras': 15, 'hid': 9},

        # --- HIDRATOS Y GRANOS ---
        'Arroz': {'cal': 360, 'prot': 7, 'gras': 1, 'hid': 78}, # Crudo promedio
        'Pasta': {'cal': 350, 'prot': 12, 'gras': 1.5, 'hid': 70}, # Cruda
        'Avena': {'cal': 389, 'prot': 16, 'gras': 6, 'hid': 66},
        'Pan': {'cal': 265, 'prot': 9, 'gras': 3.2, 'hid': 49},
        'Harina': {'cal': 364, 'prot': 10, 'gras': 1, 'hid': 76},
        'Patata': {'cal': 77, 'prot': 2, 'gras': 0.1, 'hid': 17},

        # --- LÁCTEOS Y HUEVOS ---
        'Huevos': {'cal': 155, 'prot': 13, 'gras': 11, 'hid': 1.1},
        'Leche Entera': {'cal': 61, 'prot': 3.2, 'gras': 3.3, 'hid': 4.8},
        'Leche Semi': {'cal': 45, 'prot': 3.4, 'gras': 1.5, 'hid': 4.7}, # Semidesnatada
        'Leche Desnatada': {'cal': 34, 'prot': 3.4, 'gras': 0.1, 'hid': 5},
        'Bebida de Avena': {'cal': 40, 'prot': 0.8, 'gras': 1.2, 'hid': 6}, # "Leche" vegetal
        'Queso Fresco': {'cal': 98, 'prot': 12, 'gras': 4, 'hid': 3},
        'Yogur Griego': {'cal': 120, 'prot': 3, 'gras': 10, 'hid': 4},
        'Mantequilla': {'cal': 717, 'prot': 0.9, 'gras': 81, 'hid': 0.1},

        # --- FRUTOS SECOS Y EXTRAS ---
        'Aceite de Oliva': {'cal': 884, 'prot': 0, 'gras': 100, 'hid': 0},
        'Nueces': {'cal': 654, 'prot': 15, 'gras': 65, 'hid': 14},
        'Cacahuete': {'cal': 567, 'prot': 26, 'gras': 49, 'hid': 16}, # Cubre "Crema de Cacahuete"
        
        # --- FRUTAS ---
        'Manzana': {'cal': 52, 'prot': 0.3, 'gras': 0.2, 'hid': 14},
        'Plátano': {'cal': 89, 'prot': 1.1, 'gras': 0.3, 'hid': 23},
        'Limón': {'cal': 29, 'prot': 1.1, 'gras': 0.3, 'hid': 9},
        'Naranja': {'cal': 47, 'prot': 0.9, 'gras': 0.1, 'hid': 12},

        # --- CONDIMENTOS Y OTROS (Para evitar ceros, aunque sea poco) ---
        'Sal': {'cal': 0, 'prot': 0, 'gras': 0, 'hid': 0},
        'Pimienta': {'cal': 251, 'prot': 10, 'gras': 3.3, 'hid': 64},
        'Café': {'cal': 1, 'prot': 0.1, 'gras': 0, 'hid': 0},
        'Cacao': {'cal': 228, 'prot': 20, 'gras': 14, 'hid': 58}, # Cacao puro
        'Vinagre': {'cal': 18, 'prot': 0, 'gras': 0, 'hid': 0.4},
        'Soja': {'cal': 53, 'prot': 8, 'gras': 0.6, 'hid': 4.9}, # Salsa de soja
    }

    ingredientes = IngredienteBase.objects.all()
    count = 0

    print(f"🔎 Analizando {ingredientes.count()} ingredientes en la base de datos...")

    for ing in ingredientes:
        match_encontrado = False
        
        for clave, macros in datos_nutricionales.items():
            # Buscamos la clave dentro del nombre del ingrediente
            if clave.lower() in ing.nombre.lower():
                ing.calorias = macros['cal']
                ing.proteinas = macros['prot']
                ing.grasas = macros['gras']
                ing.hidratos = macros['hid']
                ing.save()
                print(f"✅ {ing.nombre} -> {clave}")
                match_encontrado = True
                count += 1
                break 
        
        if not match_encontrado:
            # Si sigue sin encontrarse, aviso visual fuerte
            print(f"⚠️  SIN DATOS: {ing.nombre}")

    print(f"\n✨ Proceso finalizado. {count} ingredientes actualizados con éxito.")

if __name__ == "__main__":
    sembrar_nutricion()