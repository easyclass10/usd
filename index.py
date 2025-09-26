import smtplib
from email.mime.text import MIMEText
import yfinance as yf
import os  # Para leer variables de entorno

def obtener_ticket(ticket):
    ticker = yf.Ticker(ticket)
    data = ticker.history(period="1d", interval="1m")  # últimos datos del día
    if data.empty:
        raise ValueError(f"No se pudo obtener la tasa {ticket}")
    return data["Close"].iloc[-1]  # último valor de cierre

def obtener_btc():
    ticker = yf.Ticker("BTC-USD")
    data = ticker.history(period="1d", interval="1m")  # últimos datos del día
    if data.empty:
        raise ValueError("No se pudo obtener la tasa BTC")
    return data["Close"].iloc[-1]  # último valor de cierre

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

def enviar_alerta_limite(ticket,limite):
    valor=obtener_ticket(ticket)
    if valor < limite:
        asunto = f"Alerta {ticket}"
        mensaje = f"{ticket}: {valor:.2f} USD."
        try:
            enviar_correo(remitente_email, clave_aplicacion, destinatario_email, asunto, mensaje)
            print("Correo enviado correctamente.")
        except Exception as e:
            print("Error enviando correo:", e)
    else:
        print("No se envía correo. Tasa por encima del límite.")

# --- Script principal ---
if __name__ == "__main__":
    limite = 3880

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
        btc = obtener_btc()
        print(f"Tasa actual COP/USD: {tasa}")
        print(f"BTC-USD: {btc}")
    except Exception as e:
        print("Error obteniendo tasa:", e)
        exit(1)

    if tasa < limite:
        asunto = "Alerta: Dólar bajo"
        mensaje = f"El dólar está a {tasa:.2f} COP."
        try:
            enviar_correo(remitente_email, clave_aplicacion, destinatario_email, asunto, mensaje)
            print("Correo enviado correctamente.")
        except Exception as e:
            print("Error enviando correo:", e)
    else:
        print("No se envía correo. Tasa por encima del límite.")

    if btc < 108600:
        asunto = "Alerta BTC"
        mensaje = f"BTC: {btc:.2f} USD."
        try:
            enviar_correo(remitente_email, clave_aplicacion, destinatario_email, asunto, mensaje)
            print("Correo enviado correctamente.")
        except Exception as e:
            print("Error enviando correo:", e)
    else:
        print("No se envía correo. Tasa por encima del límite.")
    
    # enviar_alerta_limite(ticket,limite)
    enviar_alerta_limite("ETH-USD",4100)
    enviar_alerta_limite("BTC-USD",8000000)
