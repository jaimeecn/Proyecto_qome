import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import IngredienteBase

def sembrar_caducidades():
    print("⏳ Configurando relojes biológicos...")

    reglas = {
        2: ['salmón', 'merluza', 'carne picada', 'pollo', 'pechuga', 'lomo', 'ternera', 'ensalada', 'lechuga'],
        5: ['pimiento', 'calabacín', 'brócoli', 'zanahoria', 'tomate', 'espinacas', 'champiñones', 'jamón', 'pavo'],
        15: ['yogur', 'huevos', 'mantequilla', 'queso', 'manzana', 'naranja', 'limón', 'cebolla', 'ajo', 'patata'],
        365: ['atún', 'arroz', 'pasta', 'legumbre', 'bote', 'lata', 'harina', 'azucar', 'sal', 'aceite', 'vinagre', 'soja', 'café', 'cacao', 'avena', 'pan', 'cacahuete', 'nueces', 'congelado', 'quinoa']
    }

    ingredientes = IngredienteBase.objects.all()
    for ing in ingredientes:
        nombre = ing.nombre.lower()
        dias = 7
        for d, palabras in reglas.items():
            if any(p in nombre for p in palabras):
                dias = d
                break
        ing.dias_caducidad = dias
        ing.save()

    print("✅ Caducidades actualizadas.")

if __name__ == "__main__":
    sembrar_caducidades()