import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}
COOKIES = {'postalCode': '28001', 'warehouseId': '482'}

def imprimir_arbol_mercadona():
    print("🗺️  Descargando mapa de Mercadona...")
    
    url = "https://tienda.mercadona.es/api/categories/"
    r = requests.get(url, headers=HEADERS, cookies=COOKIES)
    
    if r.status_code != 200:
        print("❌ Error de conexión")
        return

    categorias = r.json().get('results', [])

    print("\n--- PASILLOS PRINCIPALES ---")
    for cat in categorias:
        print(f"📁 ID: {cat['id']} | NOMBRE: {cat['name']}")
        
        # Vamos a mirar un nivel más abajo (Subcategorías)
        for sub in cat.get('categories', []):
            print(f"   ↳ 📂 ID: {sub['id']} | {sub['name']}")
            
            # Y un nivel más (el detalle fino)
            for subsub in sub.get('categories', []):
                print(f"      ↳ 🏷️  ID: {subsub['id']} | {subsub['name']}")

if __name__ == "__main__":
    imprimir_arbol_mercadona()