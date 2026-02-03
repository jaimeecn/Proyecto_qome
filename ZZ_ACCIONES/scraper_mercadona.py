import os
import django
import requests
import time
from decimal import Decimal
import sys

# SETUP
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import Supermercado, IngredienteBase, ProductoReal

# --- CONFIGURACIÓN V3 ---
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# 1. MAPA DE CATEGORÍAS (Añadida SAL y WEB ID de Mercadona)
MAPA_CATEGORIAS_IDS = {
    # Carniceria / Pescaderia
    "pollo": 38, "ternera": 44, "cerdo": 37, 
    # Despensa
    "arroz": 118, "pasta": 120, "aceite": 112, "sal": 112, "atún": 122, "tomate": 126, # 126 es tomate frito/salsas
    # Frescos
    "huevos": 77, "leche": 72, "patata": 29, "lechuga": 28, "cebolla": 29, "ajo": 29, 
    "fruta": 27
}

# 2. DICCIONARIO DE TRADUCCIÓN (Receta -> Búsqueda Flexible)
# Si la receta dice "Aceite Oliva", buscamos que tenga "aceite" Y "oliva" (ignorando el "de")
KEYWORDS_FLEXIBLES = {
    "Aceite Oliva": ["aceite", "oliva"],
    "Ternera Picada": ["picada", "vacuno"], # Ojo: Mercadona usa "Vacuno" a veces en vez de Ternera
    "Atún Lata": ["atún", "aceite"], # O "natural"
    "Tomate Frito": ["tomate", "frito"],
    "Sal": ["sal", "mesa"], # Sal de mesa
    "Lechuga": ["lechuga", "iceberg"],
    "Pasta": ["macarrón", "plumas", "spaghetti", "pasta"], # Aceptamos cualquier tipo
}

def obtener_productos(cat_id):
    try:
        url = f"https://tienda.mercadona.es/api/categories/{cat_id}/?lang=es"
        r = requests.get(url, headers=HEADERS)
        data = r.json()
        productos = []
        def extraer(nodo):
            if 'products' in nodo: productos.extend(nodo['products'])
            if 'categories' in nodo: 
                for sub in nodo['categories']: extraer(sub)
        extraer(data)
        return productos
    except Exception as e: 
        print(f"Error red: {e}")
        return []

def cumple_criterios(nombre_producto, nombre_ingrediente_base):
    nombre_prod = nombre_producto.lower()
    nombre_ing = nombre_ingrediente_base.lower()

    # 1. Búsqueda por Keywords Flexibles
    if nombre_ingrediente_base in KEYWORDS_FLEXIBLES:
        palabras_clave = KEYWORDS_FLEXIBLES[nombre_ingrediente_base]
        # Deben estar TODAS las palabras clave (ej: "aceite" Y "oliva")
        return all(k in nombre_prod for k in palabras_clave)
    
    # 2. Búsqueda Default (Contiene string literal)
    return nombre_ing in nombre_prod

def ejecutar_robot():
    print("🤖 Scraper Mercadona V3 (Smart Match + Sal)...")
    mercadona, _ = Supermercado.objects.get_or_create(nombre="Mercadona", defaults={'color_brand': '#007A3E'})
    ingredientes = IngredienteBase.objects.all()

    total_importados = 0

    for ing in ingredientes:
        # Buscar ID de categoría
        cat_id = None
        for k, v in MAPA_CATEGORIAS_IDS.items():
            if k in ing.nombre.lower():
                cat_id = v
                break
        
        if not cat_id: 
            print(f"⏩ Saltando {ing.nombre} (No mapeado en IDs)")
            continue

        raw = obtener_productos(cat_id)
        
        # Filtrar candidatos
        candidatos = []
        for p in raw:
            if cumple_criterios(p['display_name'], ing.nombre):
                candidatos.append(p)
        
        # Guardar TOP 3 más baratos (para tener variedad)
        count_ing = 0
        for p in candidatos[:3]:
            try:
                info = p['price_instructions']
                precio = Decimal(info['unit_price'])
                pum = Decimal(info['reference_price']) 
                fmt = info['reference_format']
                
                # Cálculo Peso
                peso_g = 1000
                if pum > 0:
                    ratio = float(precio) / float(pum)
                    if fmt.lower() in ['kg', 'l']: peso_g = int(ratio * 1000)
                    else: peso_g = int(ratio * 1000) # Fallback unidades

                ProductoReal.objects.update_or_create(
                    nombre_comercial=p['display_name'],
                    supermercado=mercadona,
                    defaults={
                        "ingrediente_base": ing,
                        "precio_actual": precio,
                        "peso_gramos": peso_g,
                        "precio_por_kg": pum if fmt == 'kg' else (precio / Decimal(peso_g/1000) if peso_g > 0 else 0),
                        "imagen_url": p['thumbnail']
                    }
                )
                count_ing += 1
            except: pass
        
        if count_ing > 0:
            print(f"✅ {ing.nombre}: {count_ing} productos.")
        else:
            print(f"❌ {ing.nombre}: 0 productos encontrados (Revisar keywords).")
        
        total_importados += count_ing
        time.sleep(0.1)

    print(f"\n🏁 Total Global: {total_importados} productos en BD.")

if __name__ == "__main__":
    ejecutar_robot()