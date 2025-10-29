from django import forms
from .models import Nino, ResponsableAutorizado, AsignacionAula, Seccion, HorarioAula, Asistencia, PermisoAusencia


class NinoForm(forms.ModelForm):
    """Formulario para registrar y editar información de niños"""
    
    class Meta:
        model = Nino
        fields = [
            'nombre_completo', 'edad', 'fecha_nacimiento', 'genero', 'foto',
            'nombre_responsable', 'telefono_responsable', 'email_responsable', 'parentesco',
            'peso', 'altura', 'tipo_sangre',
            'alergias', 'enfermedades', 'medicamentos', 'observaciones_medicas',
            'documento_medico', 'activo'
        ]
        
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre completo del niño/a'
            }),
            'edad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '12'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-select'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'nombre_responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del responsable'
            }),
            'telefono_responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '555-1234-5678'
            }),
            'email_responsable': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'parentesco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Madre, Padre, Tutor, etc.'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Peso en kilogramos'
            }),
            'altura': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Altura en centímetros'
            }),
            'tipo_sangre': forms.Select(attrs={
                'class': 'form-select'
            }),
            'alergias': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Puede dejar el campo vacío si no tiene alergias'
            }),
            'enfermedades': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enfermedades crónicas o condiciones médicas'
            }),
            'medicamentos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medicamentos que toma regularmente'
            }),
            'observaciones_medicas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            }),
            'documento_medico': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
        labels = {
            'nombre_completo': 'Nombre Completo *',
            'edad': 'Edad (años) *',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'genero': 'Género',
            'foto': 'Foto del Niño/a',
            'nombre_responsable': 'Nombre del Responsable *',
            'telefono_responsable': 'Teléfono del Responsable *',
            'email_responsable': 'Email del Responsable',
            'parentesco': 'Parentesco *',
            'peso': 'Peso (kg)',
            'altura': 'Altura (cm)',
            'tipo_sangre': 'Tipo de Sangre',
            'alergias': 'Alergias *',
            'enfermedades': 'Enfermedades',
            'medicamentos': 'Medicamentos',
            'observaciones_medicas': 'Observaciones Médicas',
            'documento_medico': 'Documento Médico (Recetas, certificados, etc.)',
            'activo': '¿Está activo en la guardería?'
        }
    
    def clean_alergias(self):
        """Validación personalizada para el campo alergias"""
        alergias = self.cleaned_data.get('alergias', '').strip()
        # El campo puede estar vacío o tener contenido
        # Si está vacío, podríamos poner "Ninguna" o dejarlo vacío según los requisitos
        return alergias
    
    def clean_edad(self):
        """Validación personalizada para la edad"""
        edad = self.cleaned_data.get('edad')
        if edad is not None and (edad < 0 or edad > 12):
            raise forms.ValidationError("La edad debe estar entre 0 y 12 años.")
        return edad
    



    # Formulario para el responsable

class ResponsableAutorizadoForm(forms.ModelForm):
    """Formulario para registrar responsables autorizados"""
    
    # Campo oculto para la firma (se llenará con JavaScript)
    firma_electronica = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    class Meta:
        model = ResponsableAutorizado
        fields = [
            'nombre_completo', 'identificacion', 'telefono', 'email', 'relacion',
            'direccion', 'foto',
            'fecha_inicio_autorizacion', 'fecha_fin_autorizacion',
            'dias_autorizados', 'hora_inicio', 'hora_fin',
            'firma_electronica', 'observaciones', 'activo'
        ]
        
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del responsable autorizado'
            }),
            'identificacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DUI, Pasaporte, etc.'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '555-1234-5678'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'relacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tío, Abuelo, Hermano, etc.'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección completa'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'fecha_inicio_autorizacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin_autorizacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'dias_autorizados': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: L,M,X,J,V (Lunes a Viernes)'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales o restricciones'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
        labels = {
            'nombre_completo': 'Nombre Completo *',
            'identificacion': 'Número de Identificación *',
            'telefono': 'Teléfono *',
            'email': 'Correo Electrónico',
            'relacion': 'Relación con el Niño *',
            'direccion': 'Dirección',
            'foto': 'Fotografía',
            'fecha_inicio_autorizacion': 'Fecha de Inicio *',
            'fecha_fin_autorizacion': 'Fecha de Fin (opcional)',
            'dias_autorizados': 'Días Autorizados',
            'hora_inicio': 'Hora de Inicio',
            'hora_fin': 'Hora de Fin',
            'observaciones': 'Observaciones',
            'activo': 'Autorización Activa'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio_autorizacion')
        fecha_fin = cleaned_data.get('fecha_fin_autorizacion')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        
        # Validar que la fecha de fin sea posterior a la de inicio
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de fin debe ser posterior a la fecha de inicio.'
                )
        
        # Validar horarios
        if hora_inicio and hora_fin:
            if hora_fin <= hora_inicio:
                raise forms.ValidationError(
                    'La hora de fin debe ser posterior a la hora de inicio.'
                )
        
        return cleaned_data
    


# ---- PBI 03 --- 

class AsignarAulaForm(forms.ModelForm):
    class Meta:
        model = AsignacionAula
        fields = ['seccion']
        widgets = {
            'seccion': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'seccion': 'Seleccionar Aula, Sección y Maestro',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener secciones activas con sus relaciones
        secciones = Seccion.objects.filter(
            activo=True,
            aula__activo=True
        ).select_related('aula', 'maestro').order_by('aula__nombre', 'nombre')
        
        # Crear opciones personalizadas que incluyan el maestro
        choices = [('', '---------')]  # Opción vacía por defecto
        
        for seccion in secciones:
            # Obtener nombre del maestro
            if seccion.maestro:
                maestro_nombre = seccion.maestro.nombre_completo
            else:
                maestro_nombre = "Sin maestro asignado"
            
            # Formato: "Aula - Sección - Maestro: Nombre"
            texto_opcion = f"{seccion.aula.nombre} - {seccion.nombre} - Maestro: {maestro_nombre}"
            
            choices.append((seccion.id, texto_opcion))
        
        # Asignar las opciones personalizadas al campo
        self.fields['seccion'].choices = choices



class HorarioAulaForm(forms.ModelForm):
    class Meta:
        model = HorarioAula
        fields = ['dia', 'hora_inicio', 'hora_fin']
        widgets = {
            'dia': forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

# ASISTENCIA EN TIEMPO REAL

# forms.py
class AsistenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = ['presente', 'motivo_inasistencia']
        widgets = {
            'presente': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_presente'}),
            'motivo_inasistencia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Opcional: Enfermedad, cita médica, etc.'
            }),
        }
        labels = {
            'presente': '¿El niño asistió hoy?',
            'motivo_inasistencia': 'Motivo de inasistencia (opcional)',
        }

    def clean(self):
        cleaned_data = super().clean()
        presente = cleaned_data.get('presente')
        motivo = cleaned_data.get('motivo_inasistencia')

        # Si está presente, limpiar el motivo
        if presente:
            cleaned_data['motivo_inasistencia'] = None
        # Si no está presente, permitir que el motivo sea vacío → inasistencia NO justificada
        return cleaned_data


# ---- PBI 05: PERMISOS DE AUSENCIA ----

class PermisoAusenciaForm(forms.ModelForm):
    """Formulario para solicitar permisos de ausencia"""
    
    class Meta:
        model = PermisoAusencia
        fields = [
            'tipo', 'fecha_inicio', 'fecha_fin',
            'hora_inicio', 'hora_fin',
            'motivo', 'documento'
        ]
        
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa brevemente el motivo del permiso de ausencia',
                'required': True
            }),
            'documento': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            })
        }
        
        labels = {
            'tipo': 'Tipo de Permiso *',
            'fecha_inicio': 'Fecha de Inicio *',
            'fecha_fin': 'Fecha de Fin (opcional)',
            'hora_inicio': 'Hora de Inicio (opcional)',
            'hora_fin': 'Hora de Fin (opcional)',
            'motivo': 'Motivo de la Ausencia *',
            'documento': 'Comprobante (opcional)'
        }
        
        help_texts = {
            'fecha_fin': 'Dejar en blanco si es ausencia de un solo día',
            'hora_inicio': 'Solo para ausencias parciales',
            'hora_fin': 'Solo para ausencias parciales',
            'documento': 'Adjunte certificado médico, carta, etc. (formatos: PDF, JPG, PNG, DOC, DOCX)'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        
        # Validar que la fecha de fin sea posterior o igual a la de inicio
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de fin debe ser posterior o igual a la fecha de inicio.'
                )
        
        # Validar horarios si ambos están presentes
        if hora_inicio and hora_fin:
            if hora_fin <= hora_inicio:
                raise forms.ValidationError(
                    'La hora de fin debe ser posterior a la hora de inicio.'
                )
        
        # Validar que si se proporciona una hora, se proporcione la otra
        if (hora_inicio and not hora_fin) or (hora_fin and not hora_inicio):
            raise forms.ValidationError(
                'Debe proporcionar tanto la hora de inicio como la hora de fin para ausencias parciales.'
            )
        
        return cleaned_data