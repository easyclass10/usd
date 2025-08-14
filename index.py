import smtplib
from email.mime.text import MIMEText
import yfinance as yf
import os  # Para leer variables de entorno

# --- Función para obtener el valor del dólar usando yfinance ---
def obtener_tasa():
    ticker = yf.Ticker("COP=X")
    data = ticker.history(period="1d", interval="1m")  # últimos datos del día
    if data.empty:
        raise ValueError("No se pudo obtener la tasa USD/COP")
    return data["Close"].iloc[-1]  # último valor de cierre

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
    limite = 4100.0

    # Cargar secretos desde las variables de entorno
    remitente_email = os.environ.get("SENDER_EMAIL")
    clave_aplicacion = os.environ.get("APP_PASSWORD")
    destinatario_email = os.environ.get("RECIPIENT_EMAIL")
    
    # Validar que se cargaron todos los secretos
    if not all([remitente_email, clave_aplicacion, destinatario_email]):
        print("Error: Faltan variables de entorno (SENDER_EMAIL, APP_PASSWORD, RECIPIENT_EMAIL).")
        exit(1)

    try:
        tasa = obtener_tasa()
        print(f"Tasa actual COP/USD: {tasa}")
    except Exception as e:
        print("Error obteniendo tasa:", e)
        exit(1)

    # Como COP=X es pesos colombianos por dólar invertido, invertimos el valor si quieres USD→COP
    usd_cop = 1 / tasa if tasa != 0 else None
    if usd_cop is None:
        print("Error: tasa inválida.")
        exit(1)

    print(f"Tasa actual USD→COP: {usd_cop}")

    if usd_cop < limite:
        asunto = "Alerta: Dólar bajo"
        mensaje = f"El dólar está a {tasa:.2f} COP."
        try:
            enviar_correo(remitente_email, clave_aplicacion, destinatario_email, asunto, mensaje)
            print("Correo enviado correctamente.")
        except Exception as e:
            print("Error enviando correo:", e)
    else:
        print("No se envía correo. Tasa por encima del límite.")
