import os
import django
import requests
import time
from decimal import Decimal
import sys

# 1. CONFIGURACIÓN
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import Supermercado, IngredienteBase, ProductoReal

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}
COOKIES = {'postalCode': '28001', 'warehouseId': '482'}

# 2. MAPA DE CATEGORÍAS
MAPA_CATEGORIAS = {
    "pollo": 38, "pechuga": 38, "muslo": 38, "alas": 38,
    "ternera": 44, "picada": 44, "hamburguesa": 44,
    "cerdo": 37, "lomo": 37,
    "pescado": 31, "salmón": 31, "merluza": 34, "bacalao": 33, "atún": 122,
    "arroz": 118, "pasta": 120, "legumbre": 121, "garbanzo": 121, "lenteja": 121,
    "aceite": 112, "vinagre": 112, "sal": 112, "especia": 115, "pimienta": 115,
    "harina": 69, "pan": 60, "azucar": 85,
    "conserva": 122, "tomate frito": 126, "salsa": 117, "soja": 117,
    "cacao": 86, "café": 83, "avena": 78, "cereales": 78,
    "mantequilla": 75, "cacahuete": 92, "frutos secos": 133, "quinoa": 118,
    "aguacate": 27, "nueces": 133,
    "huevos": 77, "leche": 72, "yogur": 109,
    "fruta": 27, "plátano": 27, "manzana": 27, "limón": 27, "naranja": 27,
    "verdura": 29, "lechuga": 28, "ensalada": 28, "tomate": 29, 
    "cebolla": 29, "patata": 29, "ajo": 29, "pimiento": 29, 
    "calabacín": 29, "brócoli": 29, "zanahoria": 29, "espinacas": 28, "champiñones": 29,
    "tofu": 142, "vegetariano": 142
}

# 3. FILTROS BÁSICOS
KEYWORDS_ESENCIALES = {
    "Arroz Precocinado": ["vasito", "microondas", "cocido", "listo"],
    "Arroz": ["arroz"],
    "Pollo": ["pollo", "pechuga", "muslo", "filete"],
    "Ternera": ["ternera", "vacuno", "añojo", "burger"],
    "Huevos": ["huevo"],
    "Leche": ["leche"],
    "Yogur": ["yogur"],
    "Aceite": ["aceite"],
    "Salsa de Soja": ["soja"],
    "Avena": ["avena"],
    "Pasta": ["pasta", "macarrón", "espagueti", "fideo", "hélice", "plumas"],
    "Atún Lata": ["atún"],
    "Salmón": ["salmón"],
    "Merluza": ["merluza"],
    "Tofu": ["tofu"],
    "Tomate Frito": ["tomate", "frito"],
    "Cacao": ["cacao"],
    "Crema Cacahuete": ["cacahuete"]
}

GLOBAL_BAN = ["comida para", "gato", "perro", "mascota", "infantil", "bebé", "corporal", "champú"]

def obtener_productos_categoria(cat_id):
    url = f"https://tienda.mercadona.es/api/categories/{cat_id}/"
    try:
        r = requests.get(url, headers=HEADERS, cookies=COOKIES)
        if r.status_code != 200: return []
        data = r.json()
        productos = []
        def extraer(nodo):
            if 'products' in nodo: productos.extend(nodo['products'])
            if 'categories' in nodo:
                for sub in nodo['categories']: extraer(sub)
        extraer(data)
        return productos
    except: return []

def validar_basico(nombre_prod, nombre_ingrediente):
    nombre_lower = nombre_prod.lower()
    if any(ban in nombre_lower for ban in GLOBAL_BAN): return False
    
    keywords = None
    for k, v in KEYWORDS_ESENCIALES.items():
        if k.lower() in nombre_ingrediente.lower():
            keywords = v
            break
            
    if keywords:
        if not any(k in nombre_lower for k in keywords):
            return False
    elif nombre_ingrediente.lower() not in nombre_lower:
        if nombre_ingrediente.lower()[:-1] not in nombre_lower: 
            return False

    return True

def ejecutar_robot():
    print("🤖 Iniciando Scraper V9 (Recolector Masivo)...")
    mercadona, _ = Supermercado.objects.get_or_create(nombre="Mercadona")
    ingredientes = IngredienteBase.objects.all()
    
    total_guardados = 0

    for ing in ingredientes:
        cat_id = None
        for k, v in MAPA_CATEGORIAS.items():
            if k in ing.nombre.lower():
                cat_id = v
                break
        
        if not cat_id:
            print(f"⏩ {ing.nombre}: Sin categoría.")
            continue

        raw_products = obtener_productos_categoria(cat_id)
        
        candidatos_validos = []
        for p in raw_products:
            if validar_basico(p['display_name'], ing.nombre):
                candidatos_validos.append(p)

        guardados_este_ingrediente = 0
        print(f"🔎 {ing.nombre}: Encontrados {len(candidatos_validos)} candidatos...", end=" ")

        for cand in candidatos_validos[:5]: # Guardamos TOP 5
            try:
                info = cand['price_instructions']
                p_venta = Decimal(info['unit_price'])
                p_ref = Decimal(info['reference_price'])
                fmt = info['reference_format']
                nombre_real = cand['display_name']

                # Lógica de Unidades
                tipo = 'KG'
                if fmt.lower() in ['l', 'ml']: tipo = 'L'
                elif fmt.lower() in ['ud', 'dc', 'st', 'unidad']: tipo = 'UD'

                cant_pack = 1
                if "huevos" in nombre_real.lower():
                    tipo = 'UD'
                    cant_pack = 12 if ("docena" in nombre_real.lower() or p_venta > 1.8) else 6
                elif tipo == 'UD' and p_ref > 0:
                    cant_pack = max(1, round(p_venta / p_ref))

                # La lógica de peso se calcula automáticamente en models.py al guardar
                prod, created = ProductoReal.objects.update_or_create(
                    nombre_comercial=nombre_real,
                    supermercado=mercadona,
                    defaults={
                        "ingrediente_base": ing,
                        "precio_actual": p_venta,
                        "tipo_unidad": tipo,
                        "precio_por_unidad_medida": p_ref,
                        "cantidad_pack": cant_pack,
                        "imagen_url": cand['thumbnail']
                    }
                )
                guardados_este_ingrediente += 1
            except Exception as e:
                pass
        
        if guardados_este_ingrediente > 0:
            print(f"✅ {guardados_este_ingrediente}")
        else:
            print("❌ 0")
        
        total_guardados += guardados_este_ingrediente
        time.sleep(0.05)

    print(f"\n🏁 Fin. Total productos en BD: {total_guardados}")

if __name__ == "__main__":
    ejecutar_robot()