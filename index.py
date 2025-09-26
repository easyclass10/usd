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
        return f"{ticket}: {valor:.2f} USD."
    else:
        print("No se envía correo. Tasa por encima del límite.")

# --- Script principal ---
if __name__ == "__main__":
    limite = 3880
    remitente_email = os.environ.get("SENDER_EMAIL")
    clave_aplicacion = os.environ.get("APP_PASSWORD")
    destinatario_email = os.environ.get("RECIPIENT_EMAIL")
    if not all([remitente_email, clave_aplicacion, destinatario_email]):
        print("Error: Faltan variables de entorno (SENDER_EMAIL, APP_PASSWORD, RECIPIENT_EMAIL).")
        exit(1)

    tasa=obtener_tasa()
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

    lista_tickets=["BTC-USD","ETH-USD"]
    limites=[108600,3900]
    alertas = []
    for ticket, limite in zip(lista_tickets, limites):
        mensaje_alerta = enviar_alerta_limite(ticket, limite)
        if mensaje_alerta:
            alertas.append(mensaje_alerta)
            
    if alertas:
        mensaje_final = "\n".join(alertas)
        asunto = "Alertas de Criptomonedas"
        try:
            enviar_correo(remitente_email, clave_aplicacion, destinatario_email, asunto, mensaje_final)
            print("Correo con alertas enviado correctamente.")
        except Exception as e:
            print("Error enviando correo:", e)
    else:
        print("No se encontraron alertas para enviar.")
