import os
import django
import requests
import time
from decimal import Decimal
import sys

# SETUP DJANGO
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import Supermercado, IngredienteBase, ProductoReal

# --- CONFIGURACIÓN ---
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; QomeBot/1.0)'}
API_ROOT = "https://tienda.mercadona.es/api/categories/?lang=es"

# DICCIONARIO DE TRADUCCIÓN INTELIGENTE
# Ayuda al robot a entender que "Ternera Picada" es lo mismo que "Picada de Vacuno"
KEYWORDS_FLEXIBLES = {
    "Aceite Oliva": ["aceite", "oliva"],     # Match si tiene "aceite" Y "oliva" (ignora el "de")
    "Ternera Picada": ["picada", "vacuno"],  # Match si tiene "picada" O "vacuno"
    "Atún Lata": ["atún", "claro"],          # Match si tiene "atún"
    "Tomate Frito": ["tomate", "frito"],
    "Sal": ["sal", "fina"],
    "Lechuga": ["lechuga", "iceberg"],
    "Pasta": ["macarrón", "plumas", "spaghetti", "pasta", "hélices"],
    "Arroz": ["arroz"],
    "Pollo": ["pollo", "pechuga"],
    "Leche": ["leche", "entera", "semidesnatada"],
    "Huevos": ["huevos", "camperos"],
    "Patata": ["patata", "malla"],
    "Cebolla": ["cebolla"],
    "Ajo": ["ajo", "morado"]
}

def normalizar(texto):
    """Quita tildes y pone minúsculas"""
    replacements = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"))
    texto = texto.lower()
    for a, b in replacements:
        texto = texto.replace(a, b)
    return texto

def cumple_criterios_smart(nombre_producto, nombre_ingrediente_base):
    nombre_prod = normalizar(nombre_producto)
    nombre_ing = normalizar(nombre_ingrediente_base)

    # 1. Lógica Smart (Keywords)
    if nombre_ingrediente_base in KEYWORDS_FLEXIBLES:
        keywords = KEYWORDS_FLEXIBLES[nombre_ingrediente_base]
        # Casos especiales con lógica OR (ej: Ternera)
        if nombre_ingrediente_base == "Ternera Picada":
            return "vacuno" in nombre_prod and "picada" in nombre_prod
        
        # Lógica AND por defecto (deben estar todas las palabras clave)
        # Ejemplo: "Aceite" y "Oliva" deben estar presentes
        match = True
        for k in keywords:
            if normalizar(k) not in nombre_prod:
                match = False
                break
        if match: return True

    # 2. Lógica Default (Contiene string literal)
    return nombre_ing in nombre_prod

def obtener_arbol_categorias():
    try:
        r = requests.get(API_ROOT, headers=HEADERS)
        return r.json()
    except Exception as e:
        print(f"❌ Error descargando árbol: {e}")
        return []

def extraer_productos_de_categoria(cat_id):
    url = f"https://tienda.mercadona.es/api/categories/{cat_id}/?lang=es"
    try:
        r = requests.get(url, headers=HEADERS)
        data = r.json()
        productos = []
        if 'categories' in data:
            for sub in data['categories']:
                if 'products' in sub: productos.extend(sub['products'])
        elif 'products' in data:
            productos.extend(data['products'])
        return productos
    except:
        return []

def ejecutar_crawler_smart():
    print("🕷️ CRAWLER MERCADONA V4 (SMART MATCH)...")
    
    mercadona, _ = Supermercado.objects.get_or_create(nombre="Mercadona", defaults={'color_brand': '#007A3E'})
    ingredientes_db = list(IngredienteBase.objects.all())
    
    # 1. Obtener Categorías
    arbol = obtener_arbol_categorias()
    categorias_a_visitar = []
    
    def explorar_nodo(nodo):
        if not nodo.get('categories'):
            categorias_a_visitar.append(nodo['id'])
        else:
            for hijo in nodo['categories']:
                explorar_nodo(hijo)
    
    if 'results' in arbol:
        for raiz in arbol['results']:
            explorar_nodo(raiz)
    
    print(f"🌍 Escaneando {len(categorias_a_visitar)} pasillos de Mercadona...")

    total_guardados = 0
    
    # PROCESO
    for i, cat_id in enumerate(categorias_a_visitar):
        # Feedback visual simple para no llenar la consola
        if i % 10 == 0: print(f"   ⏳ Pasillo {i}/{len(categorias_a_visitar)}...")
        
        productos_raw = extraer_productos_de_categoria(cat_id)
        
        for p in productos_raw:
            nombre_prod = p['display_name']
            
            # BUSCAR MATCH EN NUESTRA DB
            for ing in ingredientes_db:
                if cumple_criterios_smart(nombre_prod, ing.nombre):
                    try:
                        info = p['price_instructions']
                        precio = Decimal(info['unit_price'])
                        pum = Decimal(info['reference_price'])
                        fmt = info['reference_format']
                        
                        peso_g = 1000
                        if pum > 0:
                            ratio = float(precio) / float(pum)
                            if fmt in ['kg', 'L']: peso_g = int(ratio * 1000)
                            else: peso_g = int(ratio * 1000)

                        ProductoReal.objects.update_or_create(
                            nombre_comercial=nombre_prod,
                            supermercado=mercadona,
                            ingrediente_base=ing, # Link match
                            defaults={
                                "precio_actual": precio,
                                "peso_gramos": peso_g,
                                "precio_por_kg": pum if fmt == 'kg' else (precio / Decimal(peso_g/1000) if peso_g > 0 else 0),
                                "imagen_url": p.get('thumbnail', '')
                            }
                        )
                        # print(f"      🎯 Match: {ing.nombre} -> {nombre_prod}")
                        total_guardados += 1
                        break # Si ya matcheó con un ingrediente, pasamos al siguiente producto
                    except: pass
        
        time.sleep(0.2) 

    print(f"\n✅ FINALIZADO. {total_guardados} productos actualizados con precios reales.")

if __name__ == "__main__":
    ejecutar_crawler_smart()