import pandas as pd
from datetime import date, timedelta
import calendar
from functions import get_date_info
from sqlalchemy import create_engine, URL
from sqlalchemy.types import *
from db_params import params


# Colocar aqui la fecha a insertar en la Base de Datos
fecha = date.today() + timedelta(days=3)

dia, mes, year = get_date_info(fecha)

df_ofertas = pd.read_excel(f'/opt/python/OfertasMDA/Docs/Oferta Enviada {dia}-{mes}-{year}.xlsx', index_col=0)

df_ofertas['fecha_oferta'] = fecha
df_ofertas.rename(columns={'Oferta(MWh)':'Oferta'},inplace=True)
df_ofertas.rename(columns={'Weekday_Number':'weekday_number'},inplace=True)
df_ofertas.rename(columns={'Hora':'hora'},inplace=True)
df_ofertas.rename(columns={'Day_Name':'day_name'},inplace=True)
df_ofertas.rename(columns={'Oferta Ajustada':'Oferta_Ajustada'},inplace=True)

df_ofertas.pop('fecha')

print(df_ofertas.head(30))

# mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
database = params()
engine = create_engine(f'mysql+mysqlconnector://{database.user}:{database.password}@{database.host}:{database.port}/{database.database}')

df_schema = {
    "id_oferta":INTEGER,
    "fecha_oferta":DATE,
    "zona_carga":VARCHAR(40),
    "elemento":VARCHAR(40),
    "weekday_number":INT,
    "hora":INT,
    "day_name":VARCHAR(40),
    "Oferta":FLOAT,
    "Oferta_Ajustada":FLOAT
}

df_ofertas.to_sql(
    'tbl_oferta_compra',
    con=engine,
    if_exists='append',
    index=False,
    dtype=df_schema
)