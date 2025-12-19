import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from core.models import IngredienteBase, ProductoReal, Receta, RecetaIngrediente

def limpiar():
    print("🧹 Iniciando limpieza profunda...")

    # Borramos en orden para evitar conflictos
    c_prod = ProductoReal.objects.all().count()
    ProductoReal.objects.all().delete()
    print(f"   🗑️  Eliminados {c_prod} productos de Mercadona antiguos.")

    c_rec_ing = RecetaIngrediente.objects.all().count()
    RecetaIngrediente.objects.all().delete()
    
    c_rec = Receta.objects.all().count()
    Receta.objects.all().delete()
    print(f"   🗑️  Eliminadas {c_rec} recetas (incluida la manual).")

    c_ing = IngredienteBase.objects.all().count()
    IngredienteBase.objects.all().delete()
    print(f"   🗑️  Eliminados {c_ing} ingredientes base sucios.")

    print("\n✨ ¡Base de datos limpia! Lista para volver a empezar.")

if __name__ == "__main__":
    limpiar()