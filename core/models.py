from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Nino(models.Model):
    """Modelo para almacenar información de los niños en la guardería"""
    
    # Información Personal (Obligatoria)
    nombre_completo = models.CharField(
        max_length=200,
        verbose_name="Nombre Completo",
        help_text="Nombre completo del niño/a"
    )
    
    edad = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(12)],
        verbose_name="Edad",
        help_text="Edad del niño/a en años"
    )
    
    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de Nacimiento",
        null=True,
        blank=True
    )
    
    genero = models.CharField(
        max_length=10,
        choices=[
            ('M', 'Masculino'),
            ('F', 'Femenino'),
            ('O', 'Otro')
        ],
        verbose_name="Género",
        null=True,
        blank=True
    )
    
    foto = models.ImageField(
        upload_to='fotos_ninos/',
        null=True,
        blank=True,
        verbose_name="Foto del Niño/a"
    )
    
    # Información del Responsable
    nombre_responsable = models.CharField(
        max_length=200,
        verbose_name="Nombre del Responsable"
    )
    
    telefono_responsable = models.CharField(
        max_length=20,
        verbose_name="Teléfono del Responsable"
    )
    
    email_responsable = models.EmailField(
        verbose_name="Email del Responsable",
        null=True,
        blank=True
    )
    
    parentesco = models.CharField(
        max_length=50,
        verbose_name="Parentesco",
        help_text="Ej: Madre, Padre, Tutor, etc."
    )
    
    # Perfil Médico
    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Peso (kg)",
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    altura = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Altura (cm)",
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    tipo_sangre = models.CharField(
        max_length=5,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        verbose_name="Tipo de Sangre",
        null=True,
        blank=True
    )
    
    alergias = models.TextField(
        verbose_name="Alergias",
        help_text="Describir todas las alergias conocidas",
        blank=True
    )
    
    enfermedades = models.TextField(
        verbose_name="Enfermedades",
        help_text="Enfermedades crónicas o condiciones médicas",
        blank=True
    )
    
    medicamentos = models.TextField(
        verbose_name="Medicamentos",
        help_text="Medicamentos que toma regularmente",
        blank=True
    )
    
    observaciones_medicas = models.TextField(
        verbose_name="Observaciones Médicas",
        blank=True
    )
    
    # Documentos Adjuntos
    documento_medico = models.FileField(
        upload_to='documentos_medicos/',
        null=True,
        blank=True,
        verbose_name="Documento Médico",
        help_text="Recetas, certificados médicos, etc."
    )
    
    # Metadatos
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el niño/a está actualmente en la guardería"
    )
    
    usuario_registro = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Registrado por"
    )
    
    class Meta:
        verbose_name = "Niño"
        verbose_name_plural = "Niños"
        ordering = ['nombre_completo']
        
    def __str__(self):
        return f"{self.nombre_completo} ({self.edad} años)"
    
    def tiene_alergias(self):
        """Verifica si el niño tiene alergias registradas"""
        return bool(self.alergias and self.alergias.strip())
    
    def tiene_medicamentos(self):
        """Verifica si el niño toma medicamentos"""
        return bool(self.medicamentos and self.medicamentos.strip())
    
    def tiene_enfermedades(self):
        """Verifica si el niño tiene enfermedades registradas"""
        return bool(self.enfermedades and self.enfermedades.strip())
    

# Modelo para los responsables

class ResponsableAutorizado(models.Model):
    """Modelo para responsables autorizados a retirar al niño"""
    
    # Relación con el niño
    nino = models.ForeignKey(
        Nino,
        on_delete=models.CASCADE,
        related_name='responsables_autorizados',
        verbose_name="Niño"
    )
    
    # Datos Personales
    nombre_completo = models.CharField(
        max_length=200,
        verbose_name="Nombre Completo"
    )
    
    identificacion = models.CharField(
        max_length=50,
        verbose_name="Número de Identificación (DUI, Pasaporte, etc.)",
        help_text="Documento de identidad"
    )
    
    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono de Contacto"
    )
    
    email = models.EmailField(
        verbose_name="Correo Electrónico",
        blank=True,
        null=True
    )
    
    relacion = models.CharField(
        max_length=100,
        verbose_name="Relación con el Niño",
        help_text="Ej: Tío, Abuelo, Hermano mayor, Amigo de la familia"
    )
    
    direccion = models.TextField(
        verbose_name="Dirección",
        blank=True,
        help_text="Dirección completa del responsable"
    )
    
    foto = models.ImageField(
        upload_to='fotos_responsables/',
        null=True,
        blank=True,
        verbose_name="Fotografía del Responsable",
        help_text="Foto para identificación"
    )
    
    # Período de Autorización
    fecha_inicio_autorizacion = models.DateField(
        verbose_name="Fecha de Inicio de Autorización"
    )
    
    fecha_fin_autorizacion = models.DateField(
        verbose_name="Fecha de Fin de Autorización",
        null=True,
        blank=True,
        help_text="Dejar en blanco si es autorización permanente"
    )
    
    # Horarios Autorizados
    DIAS_SEMANA = [
        ('L', 'Lunes'),
        ('M', 'Martes'),
        ('X', 'Miércoles'),
        ('J', 'Jueves'),
        ('V', 'Viernes'),
        ('S', 'Sábado'),
        ('D', 'Domingo'),
    ]
    
    dias_autorizados = models.CharField(
        max_length=50,
        verbose_name="Días Autorizados",
        help_text="Ej: L,M,X,J,V (Lunes a Viernes)",
        blank=True
    )
    
    hora_inicio = models.TimeField(
        verbose_name="Hora de Inicio",
        null=True,
        blank=True,
        help_text="Hora desde la cual puede retirar al niño"
    )
    
    hora_fin = models.TimeField(
        verbose_name="Hora de Fin",
        null=True,
        blank=True,
        help_text="Hora hasta la cual puede retirar al niño"
    )
    
    # Firma Electrónica
    firma_electronica = models.TextField(
        verbose_name="Firma Electrónica",
        help_text="Firma digital en formato base64",
        blank=True
    )
    
    # Observaciones
    observaciones = models.TextField(
        verbose_name="Observaciones",
        blank=True,
        help_text="Información adicional o restricciones"
    )
    
    # Estado
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si la autorización está vigente"
    )
    
    # Metadatos
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    usuario_registro = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Registrado por"
    )
    
    class Meta:
        verbose_name = "Responsable Autorizado"
        verbose_name_plural = "Responsables Autorizados"
        ordering = ['-activo', 'nombre_completo']
        
    def __str__(self):
        return f"{self.nombre_completo} - {self.relacion} de {self.nino.nombre_completo}"
    
    def tiene_firma(self):
        """Verifica si tiene firma electrónica"""
        return bool(self.firma_electronica)
    
    def autorizacion_vigente(self):
        """Verifica si la autorización está vigente según las fechas"""
        from datetime import date
        hoy = date.today()
        
        if not self.activo:
            return False
            
        if hoy < self.fecha_inicio_autorizacion:
            return False
            
        if self.fecha_fin_autorizacion and hoy > self.fecha_fin_autorizacion:
            return False
            
        return True
    
    def dias_autorizados_lista(self):
        """Retorna lista de días autorizados"""
        if self.dias_autorizados:
            dias_dict = dict(self.DIAS_SEMANA)
            dias = self.dias_autorizados.split(',')
            return [dias_dict.get(d.strip(), d) for d in dias if d.strip()]
        return []