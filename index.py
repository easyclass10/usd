# main.py modificado
import smtplib
from email.mime.text import MIMEText
import requests
import os # Importar el módulo os

# --- Función para obtener el valor del dólar ---
def obtener_tasa(api_url):
    resp = requests.get(api_url)
    resp.raise_for_status()
    data = resp.json()
    return data["rates"]["COP"]

# --- Función para enviar el correo ---
def enviar_correo(remitente, clave_app, destinatario, asunto, mensaje):
    msg = MIMEText(mensaje)
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remitente, clave_app)
        server.send_message(msg)

# --- Script principal ---
if __name__ == "__main__":
    api_url = "https://api.exchangerate-api.com/v4/latest/USD"
    limite = 4030.0

    # --- Cargar secretos desde las variables de entorno ---
    # os.environ.get('NOMBRE_DEL_SECRET')
    remitente_email = os.environ.get("SENDER_EMAIL")
    clave_aplicacion = os.environ.get("APP_PASSWORD")
    destinatario_email = os.environ.get("RECIPIENT_EMAIL")
    
    # --- Validar que los secretos se cargaron ---
    if not all([remitente_email, clave_aplicacion, destinatario_email]):
        print("Error: Faltan una o más variables de entorno (SENDER_EMAIL, APP_PASSWORD, RECIPIENT_EMAIL).")
        exit(1)

    try:
        tasa = obtener_tasa(api_url)
        print(f"Tasa actual USD→COP: {tasa}")
    except Exception as e:
        print("Error obteniendo tasa:", e)
        exit(1)

    if tasa < limite:
        asunto = "Alerta: Dólar bajo"
        mensaje = f"El dólar está a {tasa:.2f} COP, por debajo de {limite} COP."

        try:
            enviar_correo(remitente_email, clave_aplicacion, destinatario_email, asunto, mensaje)
            print("Correo enviado correctamente.")
        except Exception as e:
            print("Error enviando correo:", e)
    else:
        print("No se envía correo. Tasa por encima del límite.")
