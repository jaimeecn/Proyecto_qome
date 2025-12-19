import os
import django
import requests
import time
from decimal import Decimal

# 1. Configuración Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import Supermercado, IngredienteBase, ProductoReal

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}
COOKIES = {'postalCode': '28001', 'warehouseId': '482'}

# --- 🗺️ EL MAPA DE IDs ---
MAPA_RAW = {
    # PROTEINAS
    "Pechuga de Pollo": 38, "Huevos L": 77, "Atún en Lata (Natural)": 122,
    "Salmón Fresco": 31, "Carne Picada Ternera": 44, "Lomo de Cerdo": 37,
    "Merluza": 34, "Yogur Griego Natural": 109, "Queso Fresco Batido": 53,
    "Tofu Firme": 142, 
    
    # CARBOHIDRATOS
    "Arroz Basmati": 118, "Arroz blanco": 118, "Pasta Integral": 120,
    "Patata": 29, "Avena en Copos": 78, "Pan Integral": 60,
    "Garbanzos (Bote)": 121, "Lentejas (Bote)": 121, "Quinoa": 118,
    "Harina de Trigo": 69,

    # GRASAS
    "Aceite de Oliva Virgen Extra": 112, "Aguacate": 27, "Nueces": 133,
    "Mantequilla": 75,
    "Crema de Cacahuete": 92, # Chocolates (Aquí están las cremas de untar)

    # FRUTAS Y VERDURAS
    "Plátano": 27, "Manzana": 27, "Limón": 27, "Naranja": 27,
    "Espinacas Frescas": 28, "Lechuga Iceberg": 28, "Brócoli": 29,
    "Zanahoria": 29, "Cebolla": 29, "Tomate": 29, "Champiñones": 29,
    "Pimiento Rojo": 29, "Calabacín": 29, "Ajo": 29,

    # OTROS
    "Sal": 112, "Pimienta Negra": 115, "Tomate Frito": 126,
    "Leche Semidesnatada": 72, "Bebida de Avena": 72, "Café Molido": 83,
    "Cacao en Polvo": 86, "Vinagre": 112, "Salsa de Soja": 117
}

MAPA_NORMALIZADO = {k.lower(): v for k, v in MAPA_RAW.items()}

# --- 🧠 DICCIONARIO DE TRADUCCIÓN ---
TRADUCCIONES = {
    "garbanzos (bote)": ["garbanzo"],
    "lentejas (bote)": ["lenteja"],
    "nueces": ["nuez"],
    "crema de cacahuete": ["cacahuete", "crema"], 
    "tofu firme": ["tofu"],
    "arroz blanco": ["arroz", "redondo"],
    "huevos l": ["huevos", "l"],
    "pimiento rojo": ["pimiento", "rojo"]
}

# --- 🚫 LISTA NEGRA (PALABRAS PROHIBIDAS) ---
# Si el producto tiene estas palabras, lo descartamos
PROHIBIDAS = {
    "crema de cacahuete": ["barrita", "wafer", "helado", "galleta"],
    "atún en lata (natural)": ["aceite", "escabeche", "tomate"], # Para asegurar que sea natural
    "arroz basmati": ["microondas", "vasitos"] # Para que compre el paquete de kilo
}

def obtener_productos_del_pasillo(categoria_id):
    url = f"https://tienda.mercadona.es/api/categories/{categoria_id}/"
    try:
        r = requests.get(url, headers=HEADERS, cookies=COOKIES)
        data = r.json()
        productos = []
        def extraer(nodo):
            if 'products' in nodo: productos.extend(nodo['products'])
            if 'categories' in nodo:
                for sub in nodo['categories']: extraer(sub)
        extraer(data)
        return productos
    except:
        return []

def buscar_mejor_coincidencia(lista_productos, nombre_ingrediente):
    nombre_limpio = nombre_ingrediente.lower()
    
    # 1. Palabras clave positivas (Lo que buscamos)
    if nombre_limpio in TRADUCCIONES:
        palabras_clave = TRADUCCIONES[nombre_limpio]
    else:
        palabras_clave = nombre_limpio.replace("(", "").replace(")", "").replace("bote", "").split()
        palabras_clave = [p for p in palabras_clave if len(p) > 2] 

    # 2. Palabras clave NEGATIVAS (Lo que evitamos)
    palabras_prohibidas = PROHIBIDAS.get(nombre_limpio, [])

    mejor_producto = None
    mejor_puntuacion = 0
    menor_precio = float('inf')

    for p in lista_productos:
        nombre_p = p['display_name'].lower()
        
        # --- FILTRO DE SEGURIDAD ---
        # Si tiene una palabra prohibida, saltamos este producto inmediatamente
        tiene_prohibida = False
        for prohibida in palabras_prohibidas:
            if prohibida in nombre_p:
                tiene_prohibida = True
                break
        if tiene_prohibida:
            continue
        # ---------------------------

        puntuacion = 0
        for palabra in palabras_clave:
            if palabra in nombre_p:
                puntuacion += 1
        
        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_producto = p
            try: menor_precio = float(p['price_instructions']['unit_price'])
            except: pass
        
        elif puntuacion == mejor_puntuacion and puntuacion > 0:
            try:
                precio_actual = float(p['price_instructions']['unit_price'])
                if precio_actual < menor_precio:
                    menor_precio = precio_actual
                    mejor_producto = p
            except: pass

    if mejor_puntuacion > 0:
        return mejor_producto
    return None

def ejecutar_robot():
    print("🎯 Iniciando Scraper V5.5 (Con Filtro Anti-Barritas)...")
    
    mercadona, _ = Supermercado.objects.get_or_create(
        nombre="Mercadona", defaults={"dominio_web": "mercadona.es", "color_hex": "#008000"}
    )
    
    ingredientes = IngredienteBase.objects.all()
    encontrados = 0

    for ingrediente in ingredientes:
        print(f"🔎 Procesando: '{ingrediente.nombre}'...", end=" ")
        
        nombre_buscar = ingrediente.nombre.lower()
        id_pasillo = MAPA_NORMALIZADO.get(nombre_buscar)
        
        if not id_pasillo:
            for k, v in MAPA_NORMALIZADO.items():
                if k in nombre_buscar:
                    id_pasillo = v
                    break

        if not id_pasillo:
            print("⚠️ No tengo ID mapeado.")
            continue

        todos_productos = obtener_productos_del_pasillo(id_pasillo)
        producto_elegido = buscar_mejor_coincidencia(todos_productos, ingrediente.nombre)
        
        if producto_elegido:
            try:
                nombre_real = producto_elegido['display_name']
                precio = Decimal(producto_elegido['price_instructions']['unit_price'])
                precio_kilo = Decimal(producto_elegido['price_instructions']['bulk_price'])
                imagen = producto_elegido['thumbnail']

                ProductoReal.objects.update_or_create(
                    nombre_comercial=nombre_real,
                    supermercado=mercadona,
                    defaults={
                        "ingrediente_base": ingrediente,
                        "precio_actual": precio,
                        "precio_por_kg": precio_kilo,
                        "peso_gramos": 0,
                        "imagen_url": imagen
                    }
                )
                print(f"✅ {precio}€ ({nombre_real})")
                encontrados += 1
            except Exception as e:
                print(f"⚠️ Error guardando: {e}")
        else:
            print("⚠️ Sin coincidencia.")
        
        time.sleep(0.05)

    print(f"\n🏁 FINAL: {encontrados} ingredientes actualizados.")

if __name__ == "__main__":
    ejecutar_robot()