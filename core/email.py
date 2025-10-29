# core/email.py
import os
import logging
from sib_api_v3_sdk import ApiClient, Configuration, SendSmtpEmail, TransactionalEmailsApi
from sib_api_v3_sdk.rest import ApiException  # ← Importa ApiException

logger = logging.getLogger(__name__)

def enviar_notificacion_inasistencia(email_destino, nombre_nino):
    api_key = os.getenv("BREVO_API_KEY")
    print(f"🔑 BREVO_API_KEY cargada: {'Sí' if api_key else 'No'}")
    if not api_key:
        print("❌ ERROR: BREVO_API_KEY no configurada")
        return False

    from sib_api_v3_sdk.rest import ApiException  # ← Importa ApiException

    configuration = Configuration()
    configuration.api_key['api-key'] = api_key
    api_instance = TransactionalEmailsApi(ApiClient(configuration))
    send_smtp_email = SendSmtpEmail(
        to=[{"email": email_destino}],
        sender={"email": "ra16004@ues.edu.sv", "name": "Guardería Infantil"},
        subject=f"Inasistencia no justificada de: {nombre_nino}",
        html_content=f"""
        <h3>Guardería Infantil</h3>
        <p>Estimado(a) responsable,</p>
        <p>Se ha registrado la <strong>inasistencia</strong> de <strong>{nombre_nino}</strong> hoy, 
        <strong>sin justificación</strong>.</p>
        <p>Por favor, comuníquese con nosotros si esto fue un error.</p>
        <hr>
        <small>Este es un mensaje automático.</small>
        """
    )
    try:
        response = api_instance.send_transac_email(send_smtp_email)
        print("✅ Correo enviado exitosamente. Response:", response)
        return True
    except ApiException as e:
        print("❌ ApiException de Brevo:")
        print("   Código:", e.status)
        print("   Cuerpo:", e.body)
        return False
    except Exception as e:
        print("❌ Error inesperado:", str(e))
        return False


# ---- PBI 05: FUNCIONES DE EMAIL PARA PERMISOS DE AUSENCIA ----

def enviar_confirmacion_solicitud_permiso(email_destino, nombre_nino, fecha_inicio, tipo_permiso):
    """Envía confirmación al responsable cuando solicita un permiso de ausencia"""
    api_key = os.getenv("BREVO_API_KEY")
    
    if not api_key:
        logger.error("BREVO_API_KEY no configurada")
        return False
    
    configuration = Configuration()
    configuration.api_key['api-key'] = api_key
    api_instance = TransactionalEmailsApi(ApiClient(configuration))
    
    send_smtp_email = SendSmtpEmail(
        to=[{"email": email_destino}],
        sender={"email": "ra16004@ues.edu.sv", "name": "Guardería Infantil"},
        subject=f"Solicitud de Permiso Recibida - {nombre_nino}",
        html_content=f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #0d6efd;">Guardería Infantil</h2>
            <h3>Solicitud de Permiso Recibida</h3>
            
            <p>Estimado(a) responsable,</p>
            
            <p>Hemos recibido su solicitud de permiso de ausencia para:</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Niño/a:</strong> {nombre_nino}</p>
                <p style="margin: 5px 0;"><strong>Tipo:</strong> {tipo_permiso}</p>
                <p style="margin: 5px 0;"><strong>Fecha:</strong> {fecha_inicio}</p>
            </div>
            
            <p>Su solicitud está siendo revisada por nuestro personal. Recibirá una notificación cuando sea procesada.</p>
            
            <hr style="margin: 20px 0;">
            <small style="color: #6c757d;">Este es un mensaje automático. Por favor no responda a este correo.</small>
        </div>
        """
    )
    
    try:
        response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"✅ Confirmación enviada a {email_destino}")
        return True
    except ApiException as e:
        logger.error(f"❌ Error Brevo API: {e.status} - {e.body}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        return False


def enviar_notificacion_permiso_aprobado(email_maestro, nombre_nino, fecha_inicio, fecha_fin, tipo_permiso, motivo, horario=None):
    """Envía notificación al maestro cuando se aprueba un permiso de ausencia"""
    api_key = os.getenv("BREVO_API_KEY")
    
    if not api_key:
        logger.error("BREVO_API_KEY no configurada")
        return False
    
    configuration = Configuration()
    configuration.api_key['api-key'] = api_key
    api_instance = TransactionalEmailsApi(ApiClient(configuration))
    
    # Formatear período de ausencia
    if fecha_fin and fecha_fin != fecha_inicio:
        periodo = f"{fecha_inicio} al {fecha_fin}"
    else:
        periodo = fecha_inicio
    
    # Formatear horario si existe
    horario_html = ""
    if horario:
        horario_html = f"<p style='margin: 5px 0;'><strong>Horario:</strong> {horario}</p>"
    
    send_smtp_email = SendSmtpEmail(
        to=[{"email": email_maestro}],
        sender={"email": "ra16004@ues.edu.sv", "name": "Guardería Infantil"},
        subject=f"Permiso de Ausencia Aprobado - {nombre_nino}",
        html_content=f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #198754;">Guardería Infantil</h2>
            <h3>Permiso de Ausencia Aprobado</h3>
            
            <p>Estimado(a) maestro(a),</p>
            
            <p>Se ha aprobado el siguiente permiso de ausencia:</p>
            
            <div style="background-color: #d1e7dd; padding: 15px; border-left: 4px solid #198754; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Niño/a:</strong> {nombre_nino}</p>
                <p style="margin: 5px 0;"><strong>Tipo de Permiso:</strong> {tipo_permiso}</p>
                <p style="margin: 5px 0;"><strong>Período:</strong> {periodo}</p>
                {horario_html}
                <p style="margin: 5px 0;"><strong>Motivo:</strong> {motivo}</p>
            </div>
            
            <p>Por favor, tome nota de esta ausencia autorizada para su registro de asistencia.</p>
            
            <hr style="margin: 20px 0;">
            <small style="color: #6c757d;">Este es un mensaje automático. Por favor no responda a este correo.</small>
        </div>
        """
    )
    
    try:
        response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"✅ Notificación de aprobación enviada a {email_maestro}")
        return True
    except ApiException as e:
        logger.error(f"❌ Error Brevo API: {e.status} - {e.body}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        return False