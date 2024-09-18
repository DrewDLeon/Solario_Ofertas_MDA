import pandas as pd
from enviar_ofertas import enviar_ofertas
from functions import get_query, get_date_info, send_mail
from db_functions import get_consumo, mda, mtr
from datetime import date, timedelta
import numpy as np
import calendar
from constants import EMAIL
import warnings

warnings.filterwarnings('ignore')


# el dia a hacer request
day = date.today() + timedelta(3)
fechaNumber = day.weekday()
dayStr = day.strftime('%Y/%m/%d')
dayOferta = day.strftime('%d/%m/%Y')
query = get_query(day, dayStr)
df = get_consumo(query)

# El consumo de Little Caesars se multiplica por .98 por perdidas
df['kWh'] = np.where((df['cliente'] == 'PEQUENO CESARMEX' ), df['kWh'] * .98, df['kWh'])

# Sumamos consumo horario por RPU
df = df.groupby(['elemento','zona_carga','cliente','rpu', 'fecha','Hora'], as_index=False)['kWh'].sum()

# Creamos una columna con el consumo en MWh
df['MWh'] = df['kWh'] / 1000
df.pop('kWh')

df.sort_values(['zona_carga','elemento','cliente', 'rpu','fecha','Hora'], inplace=True)

# Sumamos de manera horaria por Cliente, asi en caso de varios RPU's en una zona de un solo cliente
df = df.groupby(['zona_carga','elemento','cliente','fecha','Hora'], as_index=False)['MWh'].sum()

# Sumamos por zona de carga
df = df.groupby(['zona_carga','elemento','fecha','Hora'], as_index=False)['MWh'].sum()

# Se crea una columna con el dia de la semana
df['Weekday_Number'] = df['fecha'].dt.day_of_week


# Sacamos el promedio x Dia de la Semana - Hora
df = df.groupby(['zona_carga','elemento','Weekday_Number','Hora'], as_index=False)['MWh'].mean()

df.sort_values(['zona_carga','elemento','Weekday_Number','Hora'], inplace=True)

df.rename(columns = {'MWh':'Oferta(MWh)'}, inplace=True)

# SOLO USAR CUANDO SE QUIERE OFERTAR COMO DOMINGO
# fecha_sunday = date.today() + timedelta(days=1)
# fechaNumber_sunday = fecha_sunday.weekday()

# Dejamos solo los valores relevantes
df = df[df['Weekday_Number'] == fechaNumber]
df.reset_index(drop=True, inplace=True)

df['fecha'] = dayStr

# Extraemos la fecha para extraer PML's
fechapml = (day - timedelta(days=7)).strftime("%Y%m%d")
df_mda = mda(fechapml)
df_mtr = mtr(fechapml)

df.sort_values(by=['zona_carga','Hora'])
df_mda.sort_values(by=['zona_carga','hora'])
df_mtr.sort_values(by=['zona_carga','hora'])

df['mda'] = df_mda['MDA']
df['mtr'] = df_mtr['MTR']

# Aqui esta la diferencia entre MDA y MTR
df['diff'] = df[['mtr','mda']].pct_change(axis=1)['mda']


# Creamos la columna de Oferta ajustada para comenzar a ajustar
df['Oferta Ajustada'] = df['Oferta(MWh)'] 

df['changed'] = False

# El MTR es mas costoso que el MDA
df['Oferta Ajustada'] = np.where((df['diff'] <= -.3 ), df['Oferta Ajustada'] * 1.20, df['Oferta Ajustada'])
df['changed'] = np.where((df['diff'] <= -.3 ), True, df['changed'])

# El MDA es mas costoso que el MTR
df['Oferta Ajustada'] = np.where((df['diff'] >= .3 ), df['Oferta Ajustada'] * .60, df['Oferta Ajustada'])
df['changed'] = np.where((df['diff'] >= .3 ), True, df['changed'])


df['Oferta Ajustada'] = np.where((df['changed'] == False ), df['Oferta Ajustada'] * .90, df['Oferta Ajustada'])



df.pop('mda')
df.pop('mtr')
df.pop('diff')
df.pop('changed')

dia, mes, year = get_date_info(day)

print(f"Ofertas Enviadas del dia {dia} de {mes} del {year}")

df.to_excel(f'/opt/python/OfertasMDA/Docs/Oferta Enviada {dia}-{mes}-{year}.xlsx')
file_path = f'/opt/python/OfertasMDA/Docs/Oferta Enviada {dia}-{mes}-{year}.xlsx'

enviar_ofertas(dia, mes, year, dayOferta)

df1 = df.groupby('zona_carga', as_index=False)[['Oferta(MWh)', 'Oferta Ajustada']].sum().round(3)

#print(df)
message = EMAIL
message += '''
<table>
    <tr>
        <th>Zona de Carga</th>
        <th>Consumo Promedio</th>
        <th>Oferta Ajustada</th>
    </tr>
'''

for i in range(len(df1)):
    zona_carga = df1['zona_carga'][i]
    promedio = df1['Oferta(MWh)'][i]
    ajustada = df1['Oferta Ajustada'][i]
    message += f"<tr><td>{zona_carga}</td><td>{promedio}</td><td>{ajustada}</td></tr>"


message += '</table>'

suma_diaria = df1['Oferta Ajustada'].sum().round(2)

# CIERRO EL HTML DEL CORREO
message += f'''
    <div>
    <p><strong>Total de MW Ofertados:</strong> {suma_diaria} MWh</p>
    <p><u><i>Atentamente: Jarvis </i>💻</u></p>
    </div>
    <div class="footer">
            &copy; Energía Solario S.A. de C.V. 2024
        </div>
    </div>
</body>
</html>
'''

print(df1)

send_mail(mensaje = message, fecha = day, file_path = file_path)

