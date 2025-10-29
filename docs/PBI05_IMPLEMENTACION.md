# PBI 05 - Sistema de Permisos de Ausencia

## Descripción
Sistema completo para que padres/tutores suban permisos de ausencia con tipo, horario, motivo y documento opcional. Al aprobar el permiso, se notifica automáticamente al maestro vía email usando Brevo API.

## Características Implementadas

### ✅ Criterios de Aceptación
- [x] Adjuntar comprobante (opcional) - Soporta PDF, JPG, PNG, DOC, DOCX
- [x] Alertas al maestro al aprobarse el permiso - Email automático vía Brevo API

### 🎯 Funcionalidades Principales

#### 1. Modelo de Datos (`PermisoAusencia`)
- **Tipos de permiso**: Médico, Familiar, Personal
- **Estados**: Pendiente, Aprobado, Rechazado
- **Campos**:
  - Relación con el niño (ForeignKey)
  - Tipo de permiso (choices)
  - Fechas de inicio y fin (con soporte para un solo día)
  - Horarios opcionales (para ausencias parciales)
  - Motivo detallado (TextField)
  - Documento adjunto opcional (FileField)
  - Estado del permiso
  - Solicitante y aprobador (Users)
  - Metadatos de auditoría (fechas de solicitud, gestión y actualización)

#### 2. Formulario de Solicitud
- **Validaciones**:
  - Fecha de fin debe ser posterior o igual a fecha de inicio
  - Hora de fin debe ser posterior a hora de inicio
  - Ambos horarios deben estar presentes para ausencias parciales
- **Campos opcionales**:
  - Fecha fin (para ausencias de un solo día)
  - Horarios (para ausencias de día completo)
  - Documento de comprobante

#### 3. Vistas Implementadas

**a) `solicitar_permiso_ausencia(request, nino_pk)` - @login_required**
- Formulario para solicitar permisos
- Guarda el solicitante automáticamente
- Envía confirmación por email al responsable
- Redirecciona al detalle del niño con mensaje de éxito

**b) `lista_permisos_ausencia(request)` - @staff_member_required**
- Lista filtrable por estado (pendiente/aprobado/rechazado/todos)
- Paginación de 15 permisos por página
- Muestra contadores por estado
- Botones para revisar permiso y ver documento
- Búsqueda por niño, tipo y estado

**c) `gestionar_permiso_ausencia(request, pk)` - @staff_member_required**
- Vista detallada del permiso
- Formulario de gestión para aprobar/rechazar
- Campo de notas opcional para comentarios
- Al aprobar:
  - Actualiza estado a "aprobado"
  - Guarda usuario aprobador y fecha de gestión
  - Obtiene maestro del niño vía `nino.asignacion_aula.seccion.maestro`
  - Envía email al maestro con detalles del permiso
- Al rechazar:
  - Actualiza estado a "rechazado"
  - Guarda notas de rechazo

#### 4. Sistema de Notificaciones Email (Brevo API)

**a) `enviar_confirmacion_solicitud_permiso(email, nombre_nino, fecha, tipo)`**
- Envía confirmación al responsable cuando solicita un permiso
- Incluye resumen del permiso solicitado
- Template HTML con diseño Bootstrap

**b) `enviar_notificacion_permiso_aprobado(email_maestro, nombre_nino, fecha_inicio, fecha_fin, tipo, motivo, horario)`**
- Envía notificación al maestro cuando se aprueba un permiso
- Incluye todos los detalles del permiso
- Diferencia entre ausencias de un día vs múltiples días
- Muestra horario si es ausencia parcial
- Template HTML con diseño Bootstrap y colores verde (aprobado)

#### 5. Templates HTML

**a) `solicitar_permiso.html`**
- Cards organizadas por secciones:
  - Detalles del permiso (tipo y motivo)
  - Período de ausencia (fechas)
  - Horarios opcionales
  - Documento de comprobante
- Alertas informativas
- Validación en el frontend
- Responsive con Bootstrap 5

**b) `lista_permisos.html`**
- Tabla responsive con información resumida
- Filtros por estado con contadores
- Badges coloridos según tipo y estado
- Paginación completa
- Botones de acción compactos
- Vista vacía con mensaje informativo

**c) `gestionar_permiso.html`**
- Vista completa del permiso con todas las secciones:
  - Información del niño y asignación académica
  - Detalles del permiso
  - Estado y metadatos
- Formulario de gestión (solo para pendientes)
- Confirmaciones JavaScript para aprobar/rechazar
- Vista de solo lectura para permisos gestionados

#### 6. Navegación e Integración

**a) Menú Principal (`base.html`)**
- Nuevo item en dropdown "Académico" (solo staff):
  - "Permisos de Ausencia" con icono
- Acceso directo a lista de permisos

**b) Detalle del Niño (`detalle_nino.html`)**
- Botón "Solicitar Permiso" en panel de acciones
- Card de "Permisos de Ausencia Recientes":
  - Tabla con últimos 5 permisos
  - Estados visuales con badges
  - Botón para solicitar primer permiso
  - Contador de permisos totales

#### 7. Panel de Administración Django

**`PermisoAusenciaAdmin`**
- Lista con campos: niño, tipo, fechas, estado, solicitante, aprobador
- Filtros por estado, tipo y fechas
- Búsqueda por niño, motivo y solicitante
- Fieldsets organizados:
  - Información del Niño
  - Detalles del Permiso
  - Estado y Gestión
  - Metadatos (colapsado)
- Auto-guardado del solicitante en nuevos registros

## Rutas Configuradas

```python
# Permisos de Ausencia
path('ninos/<int:nino_pk>/solicitar-permiso/', views.solicitar_permiso_ausencia, name='solicitar_permiso_ausencia'),
path('permisos/', views.lista_permisos_ausencia, name='lista_permisos_ausencia'),
path('permisos/<int:pk>/gestionar/', views.gestionar_permiso_ausencia, name='gestionar_permiso_ausencia'),
```

## Archivos Modificados/Creados

### Nuevos Archivos
- `core/migrations/0006_permisoausencia.py` - Migración de la base de datos
- `core/templates/solicitar_permiso.html` - Formulario de solicitud
- `core/templates/lista_permisos.html` - Lista de permisos
- `core/templates/gestionar_permiso.html` - Gestión de permisos

### Archivos Modificados
- `core/models.py` - Modelo PermisoAusencia
- `core/forms.py` - PermisoAusenciaForm con validaciones
- `core/views.py` - 3 nuevas vistas
- `core/email.py` - 2 nuevas funciones de email
- `core/urls.py` - 3 nuevas rutas
- `core/admin.py` - Registro del modelo
- `core/templates/base.html` - Link en menú
- `core/templates/detalle_nino.html` - Card de permisos y botón

## Flujo de Trabajo Completo

### 1. Solicitud de Permiso
1. Padre/tutor accede al detalle del niño
2. Click en "Solicitar Permiso"
3. Completa formulario:
   - Selecciona tipo de permiso
   - Ingresa fechas (y opcionalmente horarios)
   - Describe motivo
   - Adjunta documento (opcional)
4. Envía solicitud
5. Sistema guarda permiso con estado "pendiente"
6. Envía email de confirmación al responsable
7. Redirecciona a detalle del niño con mensaje de éxito

### 2. Revisión por Staff
1. Staff accede a "Permisos de Ausencia" desde menú
2. Ve lista filtrada (por defecto: pendientes)
3. Click en "Revisar" para ver detalles
4. Revisa información completa del permiso
5. (Opcional) Descarga documento adjunto
6. Agrega notas si es necesario
7. Click en "Aprobar" o "Rechazar"

### 3. Aprobación y Notificación
1. Sistema actualiza estado del permiso
2. Guarda usuario aprobador y fecha de gestión
3. Si se aprueba:
   - Obtiene maestro asignado al niño
   - Formatea información del permiso
   - Envía email al maestro vía Brevo API
   - Muestra mensaje de éxito con nombre del maestro
4. Si se rechaza:
   - Guarda notas de rechazo
   - Muestra mensaje de confirmación
5. Redirecciona a lista de permisos

## Consideraciones de Seguridad

- ✅ Decorador `@login_required` en solicitud de permisos
- ✅ Decorador `@staff_member_required` en gestión y lista
- ✅ Validación de permisos a nivel de vista
- ✅ CSRF protection en todos los formularios
- ✅ Sanitización de entradas de usuario
- ✅ Archivos subidos a carpeta específica con fecha `permisos_ausencia/%Y/%m/`

## Validaciones Implementadas

### En el Formulario
- Tipo de permiso requerido
- Fecha de inicio requerida
- Motivo requerido (TextField)
- Fecha fin opcional pero debe ser >= fecha inicio
- Horarios opcionales pero deben ser completos (ambos)
- Hora fin debe ser > hora inicio
- Documento acepta solo: .pdf, .jpg, .jpeg, .png, .doc, .docx

### En el Modelo
- Choices validados para tipo y estado
- Relaciones ForeignKey con CASCADE/SET_NULL apropiados
- Campos null/blank según necesidad
- Auto-generación de fechas de auditoría

## Métodos de Ayuda del Modelo

```python
def es_ausencia_parcial(self):
    """Verifica si es una ausencia parcial (con horarios)"""
    return bool(self.hora_inicio and self.hora_fin)

def es_ausencia_multiple_dias(self):
    """Verifica si es una ausencia de múltiples días"""
    return bool(self.fecha_fin and self.fecha_fin != self.fecha_inicio)

def periodo_ausencia(self):
    """Retorna el período de ausencia en formato legible"""
    # "01/01/2025 al 05/01/2025" o "01/01/2025"

def horario_ausencia(self):
    """Retorna el horario de ausencia si aplica"""
    # "08:00 - 12:00" o "Todo el día"
```

## Testing Sugerido

### Casos de Prueba Manuales
1. ✅ Solicitar permiso de un solo día sin horarios
2. ✅ Solicitar permiso de múltiples días
3. ✅ Solicitar permiso parcial con horarios
4. ✅ Adjuntar diferentes tipos de archivos
5. ✅ Filtrar permisos por estado
6. ✅ Aprobar permiso con maestro asignado
7. ✅ Aprobar permiso sin maestro asignado
8. ✅ Rechazar permiso con notas
9. ✅ Verificar emails de confirmación
10. ✅ Verificar emails de notificación al maestro

### Validaciones a Probar
- [ ] Error si fecha_fin < fecha_inicio
- [ ] Error si hora_fin <= hora_inicio
- [ ] Error si solo se proporciona una hora
- [ ] Error si formato de archivo no es válido
- [ ] Mensaje de error claro y visible
- [ ] Redirección correcta después de operaciones

## Configuración Requerida

### Variables de Entorno (.env)
```bash
BREVO_API_KEY=xkeysib-...  # Requerido para envío de emails
DEFAULT_FROM_EMAIL=ra16004@ues.edu.sv  # Email remitente
```

### Media Files
Asegurar que `MEDIA_ROOT` y `MEDIA_URL` están configurados en `settings.py`:
```python
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
```

### Permisos de Carpetas
```bash
mkdir -p media/permisos_ausencia
chmod 755 media/permisos_ausencia
```

## Próximas Mejoras (Opcional)

- [ ] Dashboard de estadísticas de permisos
- [ ] Exportar reporte de permisos a PDF/Excel
- [ ] Notificaciones push/SMS además de email
- [ ] Calendario visual de ausencias
- [ ] Integración con sistema de asistencia
- [ ] Recordatorios automáticos de permisos próximos
- [ ] Histórico de permisos por niño
- [ ] Aprobación de permisos desde email (links mágicos)

## Conclusión

El sistema de permisos de ausencia está completamente funcional y cumple con todos los criterios de aceptación del PBI-05. La implementación sigue los patrones del proyecto existente y mantiene coherencia con el resto del sistema.

**Rama**: `feature/permisos-ausencia`  
**Commit**: `feat: Implementar sistema de permisos de ausencia (PBI-05)`  
**Estado**: ✅ Listo para merge a `main`
