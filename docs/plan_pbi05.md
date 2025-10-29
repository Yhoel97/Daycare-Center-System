Plan: Permisos de Ausencia con Comprobante y Alertas
Sistema para que padres/tutores suban permisos de ausencia con tipo, horario, motivo y documento opcional. Al aprobar, notifica automáticamente al maestro via email Brevo.

Pasos:

Crear modelo PermisoAusencia en models.py con: nino (FK), tipo (choices: médico/familiar/personal), fecha_inicio/fin, hora_inicio/fin, motivo (TextField), documento (FileField a permisos_ausencia/%Y/%m/), estado (pendiente/aprobado/rechazado), solicitante/aprobado_por (User FK), metadatos. Ejecutar migración.

Crear formulario PermisoAusenciaForm en forms.py con Bootstrap 5 widgets, validación de rangos fecha/hora, accept para documentos (.pdf,.jpg,.png,.doc,.docx), campos opcionales para fecha_fin y horarios (ausencias parciales).

Implementar vistas en views.py: solicitar_permiso_ausencia(nino_pk) con @login_required que guarda permiso y envía email confirmación al responsable; lista_permisos_ausencia() con @staff_member_required filtrable por estado; gestionar_permiso_ausencia(pk) con POST para aprobar/rechazar que al aprobar obtiene maestro desde nino.asignacion_aula.seccion.maestro y envía email con detalles del permiso.

Agregar funciones email en email.py: enviar_confirmacion_solicitud_permiso(email, nombre_nino, fecha) confirma recepción al responsable; enviar_notificacion_permiso_aprobado(email_maestro, nombre_nino, fecha_inicio, fecha_fin, tipo) alerta al maestro con detalles del permiso usando Brevo API siguiendo patrón de enviar_notificacion_inasistencia().

Crear templates: solicitar_permiso.html con form Bootstrap, alert info del niño, cards para detalles/fechas/horarios, input file para documento; lista_permisos.html con tabla y btn-group para filtros (pendiente/aprobado/rechazado), botones "Revisar" y "Ver Doc"; gestionar_permiso.html con detalles completos, textarea para notas, botones aprobar/rechazar con confirm().

Configurar URLs en urls.py: /ninos/<nino_pk>/solicitar-permiso/, /permisos/, /permisos/<pk>/gestionar/. Agregar link "Permisos de Ausencia" en dropdown Académico de base.html (solo staff). Agregar card con botón y tabla de permisos recientes en detalle_nino.html.