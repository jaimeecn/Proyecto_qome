import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import Receta, RecetaIngrediente, IngredienteBase

def cargar():
    print("📖 Actualizando libro de recetas con SARTÉN...")
    
    try:
        with open('recetas_seed.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except FileNotFoundError:
        print("❌ Error: No encuentro el archivo 'recetas_seed.json'")
        return

    # PRIMERO: Borramos solo las recetas antiguas para volver a crearlas con los datos nuevos
    Receta.objects.all().delete()
    print("🗑️  Recetas antiguas borradas para actualizar datos.")

    count = 0
    for item in datos:
        print(f"🍳 Cocinando: {item['titulo']}...", end=" ")
        
        # 1. Crear Receta
        receta, created = Receta.objects.get_or_create(
            titulo=item['titulo'],
            defaults={
                "instrucciones": item['instrucciones'],
                "tiempo_preparacion": item['tiempo'],
                "es_apta_airfryer": item['airfryer'],
                "es_apta_microondas": item['microondas'],
                "es_apta_horno": item['horno'],
                "es_apta_sarten": item['sarten'] # <--- ¡NUEVO CAMPO!
            }
        )
        
        # 2. Conectar Ingredientes
        ingredientes_ok = True
        for ing in item['ingredientes']:
            ing_db = IngredienteBase.objects.filter(nombre__iexact=ing['nombre']).first()
            if ing_db:
                RecetaIngrediente.objects.create(
                    receta=receta,
                    ingrediente_base=ing_db,
                    cantidad_gramos=ing['gramos']
                )
            else:
                print(f" (❌ Falta {ing['nombre']})", end="")
                ingredientes_ok = False

        if ingredientes_ok:
            print("✅")
            count += 1
        else:
            print("⚠️")

    print(f"\n✨ ¡Menú actualizado! {count} recetas listas con sus electrodomésticos.")

if __name__ == "__main__":
    cargar()