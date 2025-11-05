from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone


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
    

    # ===== MODELOS PARA PBI 03: AULAS, MAESTROS, SECCIONES Y HORARIOS =====

class Maestro(models.Model):
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Maestro"
        verbose_name_plural = "Maestros"
        ordering = ['nombre_completo']

    def __str__(self):
        return self.nombre_completo


class Aula(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Aula")
    capacidad = models.PositiveIntegerField(verbose_name="Capacidad Máxima")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Seccion(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre de la Sección")  # Ej: "A", "Matutina"
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='secciones')
    maestro = models.ForeignKey(Maestro, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"
        ordering = ['aula', 'nombre']

    def __str__(self):
        return f"{self.aula.nombre} - {self.nombre}"


class HorarioAula(models.Model):
    DIA_SEMANA = [
        ('LUN', 'Lunes'),
        ('MAR', 'Martes'),
        ('MIE', 'Miércoles'),
        ('JUE', 'Jueves'),
        ('VIE', 'Viernes'),
        ('SAB', 'Sábado'),
    ]
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='horarios')
    dia = models.CharField(max_length=3, choices=DIA_SEMANA, verbose_name="Día de la semana")
    hora_inicio = models.TimeField(verbose_name="Hora de inicio")
    hora_fin = models.TimeField(verbose_name="Hora de fin")

    class Meta:
        verbose_name = "Horario de Aula"
        verbose_name_plural = "Horarios de Aula"
        ordering = ['seccion', 'dia', 'hora_inicio']

    def __str__(self):
        return f"{self.seccion} | {self.get_dia_display()} {self.hora_inicio}-{self.hora_fin}"


class AsignacionAula(models.Model):
    nino = models.OneToOneField(Nino, on_delete=models.CASCADE, related_name='asignacion_aula')
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Asignación de Aula"
        verbose_name_plural = "Asignaciones de Aula"

    def __str__(self):
        return f"{self.nino.nombre_completo} → {self.seccion}"
    

    
class Asistencia(models.Model):
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField(default=timezone.now)
    presente = models.BooleanField(default=True, verbose_name="¿Asistió?")
    motivo_inasistencia = models.TextField(
        blank=True,
        null=True,
        verbose_name="Motivo de inasistencia",
        help_text="Obligatorio si el niño no asistió"
    )
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Registrado por"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('nino', 'fecha')
        ordering = ['-fecha']

    def __str__(self):
        estado = "Presente" if self.presente else "Ausente"
        return f"{self.nino.nombre_completo} - {self.fecha} ({estado})"

    def justificado(self):
        return bool(self.motivo_inasistencia)


class PermisoAusencia(models.Model):
    """Modelo para gestionar permisos de ausencia con comprobante"""
    
    TIPO_PERMISO = [
        ('medico', 'Médico'),
        ('familiar', 'Familiar'),
        ('personal', 'Personal'),
    ]
    
    ESTADO_PERMISO = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    
    # Relación con el niño
    nino = models.ForeignKey(
        Nino,
        on_delete=models.CASCADE,
        related_name='permisos_ausencia',
        verbose_name="Niño"
    )
    
    # Tipo de permiso
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_PERMISO,
        verbose_name="Tipo de Permiso"
    )
    
    # Fechas
    fecha_inicio = models.DateField(
        verbose_name="Fecha de Inicio"
    )
    
    fecha_fin = models.DateField(
        verbose_name="Fecha de Fin",
        null=True,
        blank=True,
        help_text="Dejar en blanco si es ausencia de un solo día"
    )
    
    # Horarios (para ausencias parciales)
    hora_inicio = models.TimeField(
        verbose_name="Hora de Inicio",
        null=True,
        blank=True,
        help_text="Opcional: para ausencias parciales"
    )
    
    hora_fin = models.TimeField(
        verbose_name="Hora de Fin",
        null=True,
        blank=True,
        help_text="Opcional: para ausencias parciales"
    )
    
    # Motivo
    motivo = models.TextField(
        verbose_name="Motivo de la Ausencia",
        help_text="Describa brevemente el motivo del permiso"
    )
    
    # Documento adjunto (opcional)
    documento = models.FileField(
        upload_to='permisos_ausencia/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Documento de Comprobante",
        help_text="Adjunte certificado médico, carta, etc. (opcional)"
    )
    
    # Estado del permiso
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_PERMISO,
        default='pendiente',
        verbose_name="Estado"
    )
    
    # Solicitante (padre/tutor)
    solicitante = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permisos_solicitados',
        verbose_name="Solicitado por"
    )
    
    # Aprobador (staff)
    aprobado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permisos_gestionados',
        verbose_name="Gestionado por"
    )
    
    # Notas del aprobador
    notas_gestion = models.TextField(
        blank=True,
        verbose_name="Notas de Gestión",
        help_text="Comentarios del administrador"
    )
    
    # Metadatos
    fecha_solicitud = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Solicitud"
    )
    
    fecha_gestion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Gestión"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    class Meta:
        verbose_name = "Permiso de Ausencia"
        verbose_name_plural = "Permisos de Ausencia"
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Permiso {self.get_tipo_display()} - {self.nino.nombre_completo} ({self.get_estado_display()})"
    
    def es_ausencia_parcial(self):
        """Verifica si es una ausencia parcial (con horarios)"""
        return bool(self.hora_inicio and self.hora_fin)
    
    def es_ausencia_multiple_dias(self):
        """Verifica si es una ausencia de múltiples días"""
        return bool(self.fecha_fin and self.fecha_fin != self.fecha_inicio)
    
    def periodo_ausencia(self):
        """Retorna el período de ausencia en formato legible"""
        if self.es_ausencia_multiple_dias():
            return f"{self.fecha_inicio.strftime('%d/%m/%Y')} al {self.fecha_fin.strftime('%d/%m/%Y')}"
        else:
            return self.fecha_inicio.strftime('%d/%m/%Y')
    
    def horario_ausencia(self):
        """Retorna el horario de ausencia si aplica"""
        if self.es_ausencia_parcial():
            return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"
        return "Todo el día"
    

    
class PadreNino(models.Model):
    """Relación entre usuarios padre/tutor y sus niños"""
    padre = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ninos_a_cargo',
        verbose_name="Padre/Tutor"
    )
    nino = models.ForeignKey(
        Nino,
        on_delete=models.CASCADE,
        related_name='padres',
        verbose_name="Niño"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Relación Padre-Niño"
        verbose_name_plural = "Relaciones Padre-Niño"
        unique_together = ('padre', 'nino')
    
    def __str__(self):
        return f"{self.padre.get_full_name() or self.padre.username} -> {self.nino.nombre_completo}"