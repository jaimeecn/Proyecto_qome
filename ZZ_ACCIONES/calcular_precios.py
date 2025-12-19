import os
import django
from decimal import Decimal

# 1. Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import Receta, ProductoReal

def calcular_costes():
    print("🧮 Iniciando la calculadora de costes...")
    
    recetas = Receta.objects.all()
    
    for receta in recetas:
        precio_total = Decimal(0)
        ingredientes_encontrados = 0
        total_ingredientes = receta.ingredientes.count()

        print(f"\n🍳 Analizando: {receta.titulo}")

        # Recorremos cada ingrediente de la receta (ej: Huevos, Patata...)
        for linea in receta.ingredientes.all():
            ingrediente_base = linea.ingrediente_base
            gramos_necesarios = linea.cantidad_gramos
            
            # Buscamos los productos REALES asociados a este ingrediente (ordenados por precio/kg)
            productos = ProductoReal.objects.filter(ingrediente_base=ingrediente_base).order_by('precio_por_kg')
            
            if productos.exists():
                # Cogemos el más barato (el primero de la lista)
                mejor_producto = productos.first()
                precio_kg = mejor_producto.precio_por_kg
                
                # CORRECCIÓN AQUÍ: Cálculo limpio
                # Regla de tres: (PrecioKg / 1000) * Gramos
                coste = (precio_kg / 1000) * Decimal(gramos_necesarios)
                
                precio_total += coste
                
                ingredientes_encontrados += 1
                print(f"   ✅ {ingrediente_base.nombre}: {gramos_necesarios}g x {precio_kg}€/kg = {coste:.2f}€")
            else:
                print(f"   ❌ {ingrediente_base.nombre}: No hay precio en Mercadona (coste 0€)")

        # Guardamos el resultado en la receta
        receta.precio_estimado = precio_total
        receta.save()
        
        estado = "🟢 COMPLETO" if ingredientes_encontrados == total_ingredientes else "🟠 INCOMPLETO"
        print(f"💰 Precio Final: {precio_total:.2f} € ({estado})")

    print("\n✨ ¡Cálculos terminados! Refresca la web.")

if __name__ == "__main__":
    calcular_costes()