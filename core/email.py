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
    