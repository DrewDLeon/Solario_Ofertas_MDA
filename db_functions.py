import mysql.connector as mysql
from sqlalchemy import create_engine, text, URL
from sqlalchemy.types import *
import pandas as pd
from datetime import timedelta, datetime
from db_params import params

def get_consumo(q):
    query = text(q)
    #Creamos una conexion con la DB
    database = params()
    engine = create_engine(f'mysql+mysqlconnector://{database.user}:{database.password}@{database.host}:{database.port}/{database.database}')
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
        df = pd.DataFrame(results)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['tiempo'] = df['tiempo'].astype(str)
        df['tiempo'] = df['tiempo'].str.split(' ').str[2]
        df['fechayhora'] = df['fecha'].astype(str) + ' ' + df['tiempo']
        df.pop('tiempo')
        df['fechayhora'] = pd.to_datetime(df['fechayhora'])
        df['Hora'] = df['fechayhora'].dt.hour
    return df


def mda(fechapml):
    fecha = datetime.strptime(fechapml, "%Y%m%d")
    fecha1 = fecha.strftime("%Y%m%d")
    fecha2 = (fecha - timedelta(days=7)).strftime("%Y%m%d")

    print(f"pmls desde {fecha2} a {fecha1}")

    q = f'''
            SELECT 
                t1.zona_carga, 
                (t1.hora - 1) as hora, 
                AVG(t1.pz) AS MDA
            FROM 
                tbl_mda_mtr t1
            INNER JOIN 
                (SELECT DISTINCT zona_carga FROM tbl_clientes) t2 
                ON t1.zona_carga = t2.zona_carga
            WHERE 
                t1.fuente = 'mda'
                AND t1.fecha IN ({fecha1}, {fecha2})
            GROUP BY 
                t1.zona_carga, (t1.hora - 1)
    '''
    query = text(q)
    #Creamos una conexion con la DB
    database = params()
    engine = create_engine(f'mysql+mysqlconnector://{database.user}:{database.password}@{database.host}:{database.port}/{database.database}')
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
        df = pd.DataFrame(results)
    return df


def mtr(fechapml):
    fecha = datetime.strptime(fechapml, "%Y%m%d")
    fecha1 = fecha.strftime("%Y%m%d")
    fecha2 = (fecha - timedelta(days=7)).strftime("%Y%m%d")
    q = f'''
            SELECT 
                t1.zona_carga, 
                (t1.hora - 1) as hora, 
                AVG(t1.pz) AS MTR
            FROM 
                tbl_mda_mtr t1
            INNER JOIN 
                (SELECT DISTINCT zona_carga FROM tbl_clientes) t2 
                ON t1.zona_carga = t2.zona_carga
            WHERE 
                t1.fuente = 'mtr'
                AND t1.fecha IN ({fecha1}, {fecha2})
            GROUP BY 
                t1.zona_carga, (t1.hora - 1)
    '''
    query = text(q)
    #Creamos una conexion con la DB
    database = params()
    engine = create_engine(f'mysql+mysqlconnector://{database.user}:{database.password}@{database.host}:{database.port}/{database.database}')
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
        df = pd.DataFrame(results)
    return df