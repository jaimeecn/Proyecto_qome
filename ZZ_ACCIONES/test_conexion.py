import requests

# Cabeceras de navegador estándar (necesarias para que no nos echen)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

# Código postal de Madrid (necesario para ver precios)
COOKIES = {'postalCode': '28001', 'warehouseId': '482'}

def probar_puerta(nombre, url):
    print(f"📡 Probando puerta: {nombre}...")
    print(f"   URL: {url}")
    try:
        r = requests.get(url, headers=HEADERS, cookies=COOKIES, timeout=10)
        if r.status_code == 200:
            print("   ✅ ¡ABIERTA! (Status 200)")
            print(f"   Datos recibidos: {str(r.json())[:50]}...") # Muestra un trocito
            return True
        else:
            print(f"   ❌ CERRADA (Status {r.status_code})")
            return False
    except Exception as e:
        print(f"   💥 ERROR TÉCNICO: {e}")
        return False
    print("-" * 30)

# --- LAS 3 SONDAS ---

# 1. Puerta de Categorías (Suele estar siempre abierta)
probar_puerta("Categorías", "https://tienda.mercadona.es/api/categories/")

# 2. Puerta de Producto Específico (Si falla esto, nos han bloqueado la IP)
# Buscamos el producto ID 3767 (Arroz Hacendado) directamente
probar_puerta("Producto Directo (ID 3767)", "https://tienda.mercadona.es/api/products/3767")

# 3. Puerta de Búsqueda (La que nos da problemas)
# Probamos la versión v1_1 que suele ser la correcta
probar_puerta("Buscador v1_1", "https://tienda.mercadona.es/api/v1_1/products/search/?text=arroz")