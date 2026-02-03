import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import ProductoReal

def ver_datos():
    print("🕵️‍♂️ Inspeccionando productos sospechosos...")
    sospechosos = ['Salmón Fresco', 'Huevos', 'Brócoli', 'Plátano', 'Arroz']
    
    for nombre in sospechosos:
        productos = ProductoReal.objects.filter(nombre_comercial__icontains=nombre)
        for p in productos:
            print(f"\n📦 {p.nombre_comercial}")
            print(f"   - Tipo Unidad: {p.tipo_unidad}")
            print(f"   - Precio Total: {p.precio_actual}€")
            print(f"   - PUM: {p.precio_por_unidad_medida}€")
            print(f"   - Peso Calculado: {p.peso_gramos}g")
            print(f"   - Pack: {p.cantidad_pack}")

if __name__ == "__main__":
    ver_datos()