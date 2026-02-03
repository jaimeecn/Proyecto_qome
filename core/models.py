from decimal import Decimal
import re
from django.db import models
from django.contrib.auth.models import User

# --- 1. MODELO PERFIL DE USUARIO ---
class PerfilUsuario(models.Model):
    OBJETIVOS = [
        ('PERDER', 'Perder Peso'),
        ('GANAR', 'Ganar Músculo'),
        ('MANTENER', 'Mantener Peso'),
    ]
    ACTIVIDAD = [
        ('SEDENTARIO', 'Sedentario (Oficina, poco ejercicio)'),
        ('LIGERO', 'Ligero (1-3 días/sem)'),
        ('MODERADO', 'Moderado (3-5 días/sem)'),
        ('ALTO', 'Alto (6-7 días/sem)'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    edad = models.IntegerField(default=30)
    peso_kg = models.FloatField(default=70.0)
    altura_cm = models.IntegerField(default=170)
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino')], default='M')
    objetivo = models.CharField(max_length=10, choices=OBJETIVOS, default='MANTENER')
    nivel_actividad = models.CharField(max_length=10, choices=ACTIVIDAD, default='SEDENTARIO')

    # METAS NUTRICIONALES (Calculadas automáticamente)
    gasto_energetico_diario = models.IntegerField(default=2000, help_text="Calorías diarias (TDEE)")
    objetivo_proteinas = models.IntegerField(default=0, help_text="Gramos diarios")
    objetivo_grasas = models.IntegerField(default=0, help_text="Gramos diarios")
    objetivo_hidratos = models.IntegerField(default=0, help_text="Gramos diarios")

    # Logística
    presupuesto_semanal = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    
    # Electrodomésticos
    tiene_horno = models.BooleanField(default=True)
    tiene_microondas = models.BooleanField(default=True)
    tiene_airfryer = models.BooleanField(default=False)
    
    # Tiempos de cocina
    tiempo_cocina_diario = models.IntegerField(default=30)
    tiempo_cocina_finde = models.IntegerField(default=60)

    def calcular_macronutrientes(self):
        """
        Calcula TDEE y Macros basándose en la ciencia nutricional.
        """
        # 1. TMB (Harris-Benedict)
        if self.genero == 'M':
            tmb = 10 * self.peso_kg + 6.25 * self.altura_cm - 5 * self.edad + 5
        else:
            tmb = 10 * self.peso_kg + 6.25 * self.altura_cm - 5 * self.edad - 161
            
        # 2. TDEE (Nivel de Actividad)
        factores = {'SEDENTARIO': 1.2, 'LIGERO': 1.375, 'MODERADO': 1.55, 'ALTO': 1.725}
        tdee = tmb * factores.get(self.nivel_actividad, 1.2)
        
        # 3. Ajuste por Objetivo
        factor_prot = 1.5
        factor_gras = 1.0

        if self.objetivo == 'PERDER': 
            tdee -= 400
            factor_prot = 2.0 # Proteína alta para saciedad
            factor_gras = 0.8
        elif self.objetivo == 'GANAR': 
            tdee += 300
            factor_prot = 1.8
            factor_gras = 1.0
        
        # 4. Cálculo de Gramos
        gramos_proteina = int(self.peso_kg * factor_prot)
        gramos_grasas = int(self.peso_kg * factor_gras)
        
        # 5. Hidratos son el resto
        calorias_ocupadas = (gramos_proteina * 4) + (gramos_grasas * 9)
        calorias_restantes = tdee - calorias_ocupadas
        
        # Evitar negativos o valores peligrosamente bajos
        if calorias_restantes < 200: calorias_restantes = 200
        gramos_hidratos = int(calorias_restantes / 4)

        # CORRECCIÓN AQUÍ: Usamos los nombres correctos de las variables
        return int(tdee), gramos_proteina, gramos_grasas, gramos_hidratos

    def save(self, *args, **kwargs):
        # Automáticamente recalculamos todo antes de guardar
        tdee, prot, gras, hidr = self.calcular_macronutrientes()
        self.gasto_energetico_diario = tdee
        self.objetivo_proteinas = prot
        self.objetivo_grasas = gras
        self.objetivo_hidratos = hidr
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

# --- 2. MODELO INGREDIENTE BASE (Nutrición) ---
class IngredienteBase(models.Model):
    CATEGORIAS = [
        ('Fruta', 'Fruta'), ('Verdura', 'Verdura'), ('Carniceria', 'Carnicería'),
        ('Pescaderia', 'Pescadería'), ('Lacteos', 'Lácteos'), ('Despensa', 'Despensa'),
        ('Huevos', 'Huevos'), ('Otros', 'Otros')
    ]

    nombre = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='Otros')
    calorias = models.IntegerField(default=0, help_text="Kcal por 100g")
    proteinas = models.FloatField(default=0.0)
    grasas = models.FloatField(default=0.0)
    hidratos = models.FloatField(default=0.0)
    dias_caducidad = models.IntegerField(default=7, help_text="Días aprox antes de caducar")

    def __str__(self):
        return self.nombre

# --- 3. MODELO SUPERMERCADO ---
class Supermercado(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

# --- 4. MODELO PRODUCTO REAL (El del Supermercado) ---
class ProductoReal(models.Model):
    TIPO_UNIDAD_CHOICES = [
        ('KG', 'Kilogramos (Granel/Malla)'),
        ('L', 'Litros (Botellas/Bricks)'),
        ('UD', 'Unidades (Huevos, Yogures, Piezas)'),
    ]

    ingrediente_base = models.ForeignKey(IngredienteBase, on_delete=models.CASCADE, related_name='productos_disponibles')
    supermercado = models.ForeignKey(Supermercado, on_delete=models.CASCADE)
    nombre_comercial = models.CharField(max_length=200)
    
    precio_actual = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Datos de Formato
    tipo_unidad = models.CharField(max_length=2, choices=TIPO_UNIDAD_CHOICES, default='KG')
    cantidad_pack = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    precio_por_unidad_medida = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    peso_gramos = models.IntegerField(default=0, help_text="Peso neto TOTAL calculado en gramos")
    
    imagen_url = models.URLField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        LÓGICA V3: Cálculo Robusto de Peso
        1. Intenta Matemáticas (Precio Total / PUM).
        2. Intenta Regex Avanzado (Leer nombre con decimales y volúmenes).
        3. Fallback a 1000g solo si todo falla.
        """
        peso_calculado = 0

        # INTENTO 1: MATEMÁTICAS
        if self.precio_actual > 0 and self.precio_por_unidad_medida and self.precio_por_unidad_medida > 0:
            try:
                ratio = float(self.precio_actual) / float(self.precio_por_unidad_medida)
                if self.tipo_unidad in ['KG', 'L']:
                    peso_calculado = int(round(ratio, 3) * 1000)
            except:
                pass

        # INTENTO 2: REGEX AVANZADO
        if peso_calculado < 10 and self.nombre_comercial:
            peso_extraido = self._extraer_peso_regex(self.nombre_comercial)
            if peso_extraido > 0:
                peso_calculado = peso_extraido

        # GUARDADO FINAL
        if peso_calculado > 0:
            self.peso_gramos = peso_calculado
        elif self.peso_gramos == 0: 
            self.peso_gramos = 1000 

        super().save(*args, **kwargs)

    def _extraer_peso_regex(self, texto):
        texto = texto.lower().replace(',', '.')
        match_multi = re.search(r'(\d+)\s*[x]\s*(\d+[.]?\d*)\s*(kg|gr|g|l|ml|cl)', texto)
        if match_multi:
            unidades = float(match_multi.group(1))
            peso_unit = float(match_multi.group(2))
            unidad = match_multi.group(3)
            return self._convertir_a_gramos(unidades * peso_unit, unidad)

        match_simple = re.search(r'(\d+[.]?\d*)\s*(kg|gr|g|l|ml|cl)', texto)
        if match_simple:
            return self._convertir_a_gramos(float(match_simple.group(1)), match_simple.group(2))
        return 0

    def _convertir_a_gramos(self, cantidad, unidad):
        if unidad in ['kg', 'l']: return int(cantidad * 1000)
        if unidad in ['cl']: return int(cantidad * 10)
        return int(cantidad)

    def __str__(self):
        return f"{self.nombre_comercial} ({self.peso_gramos}g)"

# --- 5. MODELO RECETAS ---
class Receta(models.Model):
    titulo = models.CharField(max_length=200)
    tiempo_preparacion = models.IntegerField(help_text="Minutos")
    es_apta_sarten = models.BooleanField(default=False)
    es_apta_airfryer = models.BooleanField(default=False)
    es_apta_horno = models.BooleanField(default=False)
    es_apta_microondas = models.BooleanField(default=False)
    es_apta_tupper = models.BooleanField(default=True)
    
    # Datos calculados (se guardan para poder filtrar y ordenar rápido)
    precio_estimado = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    calorias = models.IntegerField(default=0)
    proteinas = models.FloatField(default=0.0)
    grasas = models.FloatField(default=0.0)
    hidratos = models.FloatField(default=0.0)

    def actualizar_kpis(self):
        """
        Recalcula precios y macros recorriendo los ingredientes.
        Debe llamarse después de añadir ingredientes a la receta.
        """
        total_precio = Decimal(0.0)
        total_cal = 0
        total_prot = 0.0
        total_gras = 0.0
        total_hidr = 0.0

        ingredientes = self.ingredientes.all()

        for item in ingredientes:
            gramos = item.cantidad_gramos
            base = item.ingrediente_base

            # 1. CÁLCULO DE NUTRICIÓN
            # (Valor por 100g / 100) * gramos de la receta
            if base:
                total_cal += (base.calorias / 100) * gramos
                total_prot += (base.proteinas / 100) * gramos
                total_gras += (base.grasas / 100) * gramos
                total_hidr += (base.hidratos / 100) * gramos

            # 2. CÁLCULO DE PRECIO (Buscando el producto más eficiente)
            # Buscamos productos reales ligados a este ingrediente base
            productos_disponibles = base.productos_disponibles.all()
            
            if productos_disponibles.exists():
                # Encontramos el producto con el menor precio por gramo
                mejor_opcion = None
                menor_precio_gramo = Decimal(9999)

                for prod in productos_disponibles:
                    if prod.peso_gramos > 0 and prod.precio_actual > 0:
                        precio_gramo = prod.precio_actual / Decimal(prod.peso_gramos)
                        if precio_gramo < menor_precio_gramo:
                            menor_precio_gramo = precio_gramo
                            mejor_opcion = prod
                
                # Si encontramos precio válido, sumamos al coste de la receta
                if mejor_opcion:
                    coste_ingrediente = menor_precio_gramo * Decimal(gramos)
                    total_precio += coste_ingrediente
            else:
                # Si no hay producto real linkeado (ej. "Sal"), asumimos coste 0 o un estándar
                pass

        # Guardamos los resultados en el modelo
        self.precio_estimado = total_precio # Django redondea al guardar en DecimalField
        self.calorias = int(total_cal)
        self.proteinas = round(total_prot, 1)
        self.grasas = round(total_gras, 1)
        self.hidratos = round(total_hidr, 1)
        self.save()
    
    @property
    def calorias_totales(self):
        """Devuelve el valor ya calculado para que el HTML antiguo funcione"""
        return self.calorias
    
    def __str__(self):
        return f"{self.titulo} ({self.calorias} kcal - {self.precio_estimado}€)"

# --- 6. INGREDIENTES DE UNA RECETA ---
class RecetaIngrediente(models.Model):
    receta = models.ForeignKey(Receta, related_name='ingredientes', on_delete=models.CASCADE)
    ingrediente_base = models.ForeignKey(IngredienteBase, on_delete=models.CASCADE)
    cantidad_gramos = models.IntegerField()

    def __str__(self):
        return f"{self.ingrediente_base.nombre} ({self.cantidad_gramos}g)"

# --- 7. PLAN SEMANAL ---
class PlanSemanal(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    creado_en = models.DateTimeField(auto_now_add=True)
    lista_compra_generada = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Plan {self.fecha_inicio} - {self.usuario.username}"

class ComidaPlanificada(models.Model):
    MOMENTOS = [('COMIDA', 'Comida'), ('CENA', 'Cena')]
    DIAS = [(0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')]

    plan = models.ForeignKey(PlanSemanal, related_name='comidas', on_delete=models.CASCADE)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    dia_semana = models.IntegerField(choices=DIAS)
    momento = models.CharField(max_length=10, choices=MOMENTOS)

    class Meta:
        ordering = ['dia_semana', 'momento']