import os
import django

# 1. Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import IngredienteBase

def crear_ingredientes():
    print("🛒 Llenando la despensa con ingredientes base...")

    # Lista de 50 ingredientes comunes organizados por categoría
    lista_ingredientes = [
        # PROTEINAS
        ("Pechuga de Pollo", "Carniceria"),
        ("Huevos L", "Huevos"),
        ("Atún en Lata (Natural)", "Conservas"),
        ("Salmón Fresco", "Pescaderia"),
        ("Carne Picada Ternera", "Carniceria"),
        ("Lomo de Cerdo", "Carniceria"),
        ("Tofu Firme", "Otros"),
        ("Merluza", "Pescaderia"),
        ("Yogur Griego Natural", "Lacteos"),
        ("Queso Fresco Batido", "Lacteos"),
        
        # CARBOHIDRATOS
        ("Arroz Basmati", "Despensa"),
        ("Arroz blanco", "Despensa"),
        ("Pasta Integral", "Despensa"),
        ("Patata", "Verdura"),
        ("Avena en Copos", "Despensa"),
        ("Pan Integral", "Panaderia"),
        ("Garbanzos (Bote)", "Conservas"),
        ("Lentejas (Bote)", "Conservas"),
        ("Quinoa", "Despensa"),
        ("Harina de Trigo", "Despensa"),

        # GRASAS
        ("Aceite de Oliva Virgen Extra", "Despensa"),
        ("Aguacate", "Fruta"),
        ("Nueces", "Despensa"),
        ("Crema de Cacahuete", "Despensa"),
        ("Mantequilla", "Lacteos"),

        # FRUTAS Y VERDURAS
        ("Plátano", "Fruta"),
        ("Manzana", "Fruta"),
        ("Espinacas Frescas", "Verdura"),
        ("Brócoli", "Verdura"),
        ("Zanahoria", "Verdura"),
        ("Cebolla", "Verdura"),
        ("Tomate", "Verdura"),
        ("Lechuga Iceberg", "Verdura"),
        ("Champiñones", "Verdura"),
        ("Pimiento Rojo", "Verdura"),
        ("Calabacín", "Verdura"),
        ("Ajo", "Verdura"),
        ("Limón", "Fruta"),
        ("Naranja", "Fruta"),

        # OTROS / CONDIMENTOS
        ("Sal", "Despensa"),
        ("Pimienta Negra", "Despensa"),
        ("Tomate Frito", "Conservas"),
        ("Leche Semidesnatada", "Lacteos"),
        ("Bebida de Avena", "Lacteos"),
        ("Café Molido", "Despensa"),
        ("Cacao en Polvo", "Despensa"),
        ("Vinagre", "Despensa"),
        ("Salsa de Soja", "Despensa")
    ]

    count = 0
    for nombre, categoria in lista_ingredientes:
        # get_or_create evita duplicados si lo ejecutas varias veces
        obj, created = IngredienteBase.objects.get_or_create(
            nombre=nombre,
            defaults={'categoria': categoria}
        )
        if created:
            print(f"   ✅ Creado: {nombre}")
            count += 1
        else:
            print(f"   ⚠️ Ya existe: {nombre}")

    print(f"\n✨ ¡Proceso terminado! Se han añadido {count} ingredientes nuevos.")

if __name__ == "__main__":
    crear_ingredientes()