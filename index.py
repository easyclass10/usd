7import smtplib
from email.mime.text import MIMEText
import requests
import time

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
    limite = 4027.0

    remitente = "easyclass.1help@gmail.com"
    clave_app = "dcnp ycfv qgqq aoqe"  # Clave de aplicación de Google
    destinatario = "casgereda.1@gmail.com"
    asunto = "Alerta: Dólar bajo"

    while True:
        try:
            tasa = obtener_tasa(api_url)
            print(f"Tasa actual USD→COP: {tasa}")
        except Exception as e:
            print("Error obteniendo tasa:", e)
            time.sleep(60)  # Espera 1 min antes de intentar de nuevo
            continue

        if tasa < limite:
            mensaje = f"El dólar está a {tasa:.2f} COP, por debajo de {limite} COP."
            try:
                enviar_correo(remitente, clave_app, destinatario, asunto, mensaje)
                print("Correo enviado correctamente.")
            except Exception as e:
                print("Error enviando correo:", e)
        
        # Espera antes de volver a consultar (ej. 30 min = 1800 seg)
        time.sleep(60)
