import os
import django
import sys

# Setup de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import Receta

def calcular_macros():
    print("👨‍🍳 Calculando información nutricional de las recetas...")
    
    recetas = Receta.objects.all()
    count = 0

    for receta in recetas:
        # Reiniciamos contadores
        total_cal = 0
        total_prot = 0
        total_gras = 0
        total_hid = 0
        
        ingredientes_receta = receta.ingredientes.all()
        
        if not ingredientes_receta:
            print(f"⚠️  {receta.titulo} no tiene ingredientes. Saltando.")
            continue

        print(f"🍳 Cocinando datos para: {receta.titulo}")

        for item in ingredientes_receta:
            # item.ingrediente_base es el ingrediente (ej: Pollo)
            # item.cantidad_gramos es cuánto usas (ej: 200g)
            
            base = item.ingrediente_base
            cantidad_factor = item.cantidad_gramos / 100.0 # Porque los macros son por 100g

            # Sumamos
            total_cal += float(base.calorias) * cantidad_factor
            total_prot += float(base.proteinas) * cantidad_factor
            total_gras += float(base.grasas) * cantidad_factor
            total_hid += float(base.hidratos) * cantidad_factor

        # Guardamos en la receta
        receta.calorias_totales = round(total_cal, 2)
        receta.proteinas_totales = round(total_prot, 2)
        receta.grasas_totales = round(total_gras, 2)
        receta.hidratos_totales = round(total_hid, 2)
        receta.save()
        count += 1

    print(f"\n✅ Hecho. {count} recetas actualizadas con Macros calculados.")

if __name__ == "__main__":
    calcular_macros()