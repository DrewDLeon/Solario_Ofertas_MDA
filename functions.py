from datetime import date, timedelta
import calendar
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
load_dotenv()

def get_query(bid_date, bid_date_str):
    print(f"Simulando {bid_date_str}")
    lastDay = (bid_date - timedelta(1)).strftime('%Y%m%d')
    firstDay = (bid_date - timedelta(15)).strftime('%Y%m%d')
    query = f'''
            SELECT tcl.zona_carga, tcl.elemento, tcl.cliente, tcl.rpu, tlr.Fecha as fecha, tlr.Hora as tiempo, tlr.KWhe as kWh
            FROM tbl_clientes tcl INNER JOIN tbl_lecturas_rmu tlr
            ON tcl.id_cliente = tlr.id_cliente
            WHERE (tlr.Fecha >= {firstDay} AND tlr.Fecha <= {lastDay} AND tcl.cliente != 'Metsa')
            ORDER BY tcl.zona_carga, tlr.Fecha, tlr.Hora
    '''
    return query


def get_date_info(fecha):
        dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


        fechaNumber = fecha.weekday()
        MonthNumber = fecha.month
        dia = fecha.day
        mes = meses[MonthNumber-1]
        year = fecha.year


        return dia, mes, year


def send_mail(mensaje, fecha, file_path):
    email = os.environ.get('MAIL_EMAIL')
    contrasena = os.environ.get('MAIL_PASSWORD')
    sender_email = 'andres@solario.mx'
    # 'christian@solario.mx', 'humberto@solario.mx', 'miguel@solario.mx', 'fernando@solario.mx'
    recipient_emails = ['andres@solario.mx', 'christian@solario.mx', 'jonathan@solario.mx']
    #recipient_emails = ['andleon.castilleja@gmail.com']
    asunto = f'Solario - Ofertas de Compra de Energia en el MDA {fecha}'

    # Create the MIMEMultipart object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(recipient_emails)
    msg['Subject'] = asunto

    # Attach the body of the email
    msg.attach(MIMEText(mensaje, 'html'))

    # Check if file_path is not None and file exists
    if file_path and os.path.isfile(file_path):
        # Prepare the attachment
        filename = os.path.basename(file_path)
        attachment = open(file_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(part)

    # Establish a connection to the SMTP server
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Start TLS for security
            server.login(email, contrasena)  # Login to the email server
            server.sendmail(sender_email, recipient_emails, msg.as_string())  # Send the email
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")