#from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Nino, ResponsableAutorizado
from .models import Maestro, Aula, Seccion, HorarioAula, AsignacionAula


@admin.register(Nino)
class NinoAdmin(admin.ModelAdmin):
    """Configuración del panel de administración para Niños"""
    
    list_display = [
        'nombre_completo', 
        'edad', 
        'nombre_responsable', 
        'telefono_responsable',
        'tiene_alergias',
        'activo',
        'fecha_registro'
    ]
    
    list_filter = [
        'activo',
        'edad',
        'genero',
        'tipo_sangre',
        'fecha_registro'
    ]
    
    search_fields = [
        'nombre_completo',
        'nombre_responsable',
        'telefono_responsable',
        'email_responsable'
    ]
    
    readonly_fields = [
        'fecha_registro',
        'fecha_actualizacion',
        'usuario_registro'
    ]
    
    fieldsets = (
        ('Información Personal', {
            'fields': (
                'nombre_completo',
                'edad',
                'fecha_nacimiento',
                'genero',
                'foto'
            )
        }),
        ('Responsable', {
            'fields': (
                'nombre_responsable',
                'parentesco',
                'telefono_responsable',
                'email_responsable'
            )
        }),
        ('Perfil Médico', {
            'fields': (
                'peso',
                'altura',
                'tipo_sangre',
                'alergias',
                'enfermedades',
                'medicamentos',
                'observaciones_medicas',
                'documento_medico'
            ),
            'classes': ('collapse',)
        }),
        ('Estado y Metadatos', {
            'fields': (
                'activo',
                'usuario_registro',
                'fecha_registro',
                'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """Guarda el usuario que registra el niño"""
        if not change:  # Si es un nuevo registro
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)
    
    # Personalizar columnas con iconos
    def tiene_alergias(self, obj):
        return "✓" if obj.tiene_alergias() else "✗"
    tiene_alergias.short_description = "Alergias"
    tiene_alergias.boolean = True


    #------------------------
    ###Responsable Autorizado 
    #------------------------

@admin.register(ResponsableAutorizado)
class ResponsableAutorizadoAdmin(admin.ModelAdmin):
    """Configuración del panel de administración para Responsables Autorizados"""
    
    list_display = [
        'nombre_completo',
        'nino',
        'relacion',
        'telefono',
        'autorizacion_vigente',
        'activo',
        'fecha_registro'
    ]
    
    list_filter = [
        'activo',
        'relacion',
        'fecha_inicio_autorizacion',
        'fecha_fin_autorizacion'
    ]
    
    search_fields = [
        'nombre_completo',
        'identificacion',
        'telefono',
        'email',
        'nino__nombre_completo'
    ]
    
    readonly_fields = [
        'fecha_registro',
        'fecha_actualizacion',
        'usuario_registro'
    ]
    
    fieldsets = (
        ('Información del Niño', {
            'fields': ('nino',)
        }),
        ('Datos Personales', {
            'fields': (
                'nombre_completo',
                'identificacion',
                'telefono',
                'email',
                'relacion',
                'direccion',
                'foto'
            )
        }),
        ('Período de Autorización', {
            'fields': (
                'fecha_inicio_autorizacion',
                'fecha_fin_autorizacion',
                'dias_autorizados',
                'hora_inicio',
                'hora_fin'
            )
        }),
        ('Firma y Observaciones', {
            'fields': (
                'firma_electronica',
                'observaciones'
            ),
            'classes': ('collapse',)
        }),
        ('Estado y Metadatos', {
            'fields': (
                'activo',
                'usuario_registro',
                'fecha_registro',
                'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """Guarda el usuario que registra el responsable"""
        if not change:
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)
    
    def autorizacion_vigente(self, obj):
        return "✓" if obj.autorizacion_vigente() else "✗"
    autorizacion_vigente.short_description = "Vigente"
    autorizacion_vigente.boolean = True


    # ----- PBI-03 ----

@admin.register(Maestro)
class MaestroAdmin(admin.ModelAdmin):
        list_display = ['nombre_completo', 'email', 'telefono', 'activo']
        list_filter = ['activo']
        search_fields = ['nombre_completo', 'email']


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
        list_display = ['nombre', 'capacidad', 'activo']
        list_filter = ['activo']


@admin.register(HorarioAula)
class HorarioAulaAdmin(admin.ModelAdmin):
    list_display = ['seccion', 'dia', 'hora_inicio', 'hora_fin']
    list_filter = ['seccion__aula', 'dia']

class HorarioAulaInline(admin.TabularInline):
    model = HorarioAula
    extra = 2  # Número de formularios vacíos para horarios
    fields = ['dia', 'hora_inicio', 'hora_fin']
    # Opcional: valida que los horarios no se solapen (más adelante)

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
        list_display = ['nombre', 'aula', 'maestro', 'activo']
        list_filter = ['aula', 'maestro', 'activo']
        search_fields = ['nombre', 'aula__nombre']
        inlines = [HorarioAulaInline]  # ← Esto permite agregar horarios al editar una sección




@admin.register(AsignacionAula)
class AsignacionAulaAdmin(admin.ModelAdmin):
        list_display = ['nino', 'seccion', 'fecha_asignacion']
        list_filter = ['seccion__aula', 'seccion__maestro']
        search_fields = ['nino__nombre_completo']