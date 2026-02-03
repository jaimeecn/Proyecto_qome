import os
import django
import sys
import json 
import random
from datetime import date, timedelta
from django.db.models import F

# 1. SETUP DJANGO
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qome_backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Receta, PlanSemanal, ComidaPlanificada, ProductoReal

def generar_tetris(usuario_nombre="admin"):
    print(f"🧩 Tetris V7: Memoria a Corto Plazo (Anti-Repetición)...")
    
    try:
        user = User.objects.get(username=usuario_nombre)
    except User.DoesNotExist:
        print(f"❌ Usuario '{usuario_nombre}' no encontrado.")
        return

    # Limpieza y preparación del plan
    lunes_proximo = date.today() + timedelta(days=(7 - date.today().weekday()))
    plan, _ = PlanSemanal.objects.get_or_create(usuario=user, fecha_inicio=lunes_proximo)
    plan.comidas.all().delete()
    plan.lista_compra_generada = ""
    plan.save()

    despensa = {} 
    cesta_compra_real = {}
    
    # --- 🧠 MEMORIA DEL ALGORITMO ---
    # Guardaremos los títulos de las últimas recetas para no repetirlas
    memoria_reciente = [] 
    LIMITE_MEMORIA = 5 # No repetir nada que se haya comido en las últimas 5 comidas (2.5 días)

    dias = range(7)
    momentos = ['COMIDA', 'CENA']

    for dia in dias:
        for momento in momentos:
            print(f"\n🔎 Día {dia} ({momento})...")
            receta_elegida = None
            ingrediente_urgente = None

            # 1. BUSCAR URGENCIAS (Caducidad)
            # Prioridad: Gastar lo que se va a poner malo en < 3 días
            for ing_nombre, datos in despensa.items():
                if datos['stock'] <= 50: continue
                vida = datos['vida_util']
                dias_abierto = dia - datos['dia_apertura']
                
                # Si le queda poco de vida, es urgente
                if vida < 10 and dias_abierto >= (vida - 2):
                    ingrediente_urgente = ing_nombre
                    print(f"   🚨 URGENCIA: {ing_nombre} caduca pronto.")
                    break

            # 2. SELECCIÓN DE CANDIDATAS
            # Base: Todas las recetas
            candidatas = Receta.objects.all()

            # FILTRO 1: ANTI-REPETICIÓN (La clave del arreglo)
            if memoria_reciente:
                candidatas = candidatas.exclude(titulo__in=memoria_reciente)

            # ELEGIR RECETA
            if ingrediente_urgente:
                # Si hay urgencia, filtramos por ingrediente, PERO respetando la memoria si es posible
                subset_urgente = candidatas.filter(ingredientes__ingrediente_base__nombre=ingrediente_urgente)
                if subset_urgente.exists():
                    receta_elegida = subset_urgente.order_by('?').first()
                else:
                    # Si la única forma de gastar la urgencia es repetir plato, ¿lo permitimos?
                    # Por ahora NO, preferimos tirar comida que aburrirnos (regla de negocio)
                    # O buscamos en todas (saltando memoria) si es crítico.
                    # Vamos a ser estrictos: No repetimos. La urgencia esperará.
                    pass

            if not receta_elegida:
                # Variabilidad: Intentar gastar abiertos (ahorro) pero sin urgencia
                abiertos = [k for k, v in despensa.items() if v['stock'] > 50]
                
                # 40% de probabilidad de buscar algo que use sobras, 60% de abrir algo nuevo (para variar)
                if abiertos and random.random() > 0.6:
                    subset_ahorro = candidatas.filter(ingredientes__ingrediente_base__nombre__in=abiertos)
                    if subset_ahorro.exists(): 
                        receta_elegida = subset_ahorro.order_by('?').first()
                
                # Si no hemos elegido aún (o no hay sobras), cogemos cualquiera válida
                if not receta_elegida and candidatas.exists():
                    receta_elegida = candidatas.order_by('?').first()

            # 3. PROCESAR RECETA ELEGIDA
            if receta_elegida:
                print(f"   🍽️  {receta_elegida.titulo}")
                
                # ACTUALIZAR MEMORIA
                memoria_reciente.append(receta_elegida.titulo)
                if len(memoria_reciente) > LIMITE_MEMORIA:
                    memoria_reciente.pop(0) # Olvidamos la más antigua
                
                # GESTIÓN DE INGREDIENTES Y COMPRA
                for item in receta_elegida.ingredientes.all():
                    nombre_base = item.ingrediente_base.nombre
                    categoria = item.ingrediente_base.categoria
                    necesario = item.cantidad_gramos
                    caducidad = item.ingrediente_base.dias_caducidad
                    
                    if nombre_base not in despensa:
                        despensa[nombre_base] = {'stock': 0, 'dia_apertura': -1, 'vida_util': caducidad}

                    while despensa[nombre_base]['stock'] < necesario:
                        # --- SELECCIÓN INTELIGENTE DEL PRODUCTO ---
                        candidatos = ProductoReal.objects.filter(ingrediente_base=item.ingrediente_base)
                        
                        prod = None
                        if candidatos.exists():
                            # Prioridad: PUM más bajo
                            mejores = candidatos.exclude(precio_por_unidad_medida__lte=0).exclude(precio_por_unidad_medida__isnull=True)
                            if mejores.exists():
                                prod = mejores.order_by('precio_por_unidad_medida').first()
                            else:
                                prod = candidatos.order_by('precio_actual').first()
                        
                        # Datos del producto
                        # NOTA: Aquí el peso_pack puede ser 1000 si el scraper falló (lo arreglaremos en el siguiente paso)
                        peso_pack = prod.peso_gramos if (prod and prod.peso_gramos > 0) else 1000
                        tipo_unidad = prod.tipo_unidad if prod else 'KG'
                        cant_pack = prod.cantidad_pack if prod else 1
                        nombre_comercial = prod.nombre_comercial if prod else nombre_base
                        
                        # Añadir stock
                        despensa[nombre_base]['stock'] += peso_pack
                        
                        # Guardar en cesta (Agrupada por nombre comercial)
                        clave_cesta = nombre_comercial
                        if clave_cesta not in cesta_compra_real:
                            cesta_compra_real[clave_cesta] = {
                                'unidades': 0,
                                'peso_total_g': 0,
                                'formato_visual': tipo_unidad,
                                'cantidad_por_pack': float(cant_pack),
                                'categoria': categoria if categoria else 'Varios',
                                'ingrediente_base': nombre_base
                            }
                        
                        cesta_compra_real[clave_cesta]['unidades'] += 1
                        cesta_compra_real[clave_cesta]['peso_total_g'] += peso_pack
                        
                        # print(f"      🛒 COMPRA: {nombre_comercial[:20]}... ({peso_pack}g)")

                    despensa[nombre_base]['stock'] -= necesario
                    if despensa[nombre_base]['dia_apertura'] == -1:
                        despensa[nombre_base]['dia_apertura'] = dia 

                ComidaPlanificada.objects.create(plan=plan, receta=receta_elegida, dia_semana=dia, momento=momento)
            else:
                print("   ⚠️ No se encontró receta válida (Restricciones muy estrictas o falta de recetas).")

    # GUARDAR JSON
    plan.lista_compra_generada = json.dumps(cesta_compra_real)
    plan.save()
    print("\n✨ Plan V7 completado.")

if __name__ == "__main__":
    generar_tetris()