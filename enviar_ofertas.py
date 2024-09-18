import requests
from dotenv import load_dotenv
import json
import pandas as pd
import os


def enviar_ofertas(dia, mes, year, fecha):
    load_dotenv()
    SOLARIO_KEY = os.environ.get('SOLARIO_KEY')

    df1 = pd.read_excel(f'/opt/python/OfertasMDA/Docs/Oferta Enviada {dia}-{mes}-{year}.xlsx')

    df1.pop('diff')
    df1.pop('changed')

    userNameToken = os.environ.get('CENACE_MAIL')
    passwordToken = os.environ.get('CENACE_PASSWORD')
    huellaDigital = os.environ.get('CENACE_HD')

    print(fecha)
    fechaInicial = fecha
    fechaFinal = fecha
    clvSistema = 'SIN'

    URL_BID = os.environ.get('URL_BID')

    headers = {
        'Content-Type': 'application/soap+xml; charset=utf-8',
        'Host': 'ws01.cenace.gob.mx',
        'Content-Length': 'length',
    }

    bid_list = []
    for i in df1.index: #Tamaño del dataframe
        if df1['Hora'][i] == 23:
            elemento = df1['elemento'][i]
            bid_step = {
                "demandaFijaMw":df1['Oferta Ajustada'][i], # df1['Oferta(MWh)'][i]
                "hora":int(df1['Hora'][i])+1,
                "idSubInt":1,
                "oiMw01":0,
                "oiPrecio01":0,
                "oiMw02":0,
                "oiPrecio02":0,
                "oiMw03":0,
                "oiPrecio03":0,
            }
            bid_list.append(bid_step)

            bid_dict = {"ofertaEconomica":bid_list}
            bid_OE = json.dumps(bid_dict, indent=2)
            payload = f"""<?xml version='1.0' encoding='utf-8'?>
            <soap12:Envelope xmlns:xsi='"http://www.w3.org/2001/XMLSchema-instance"' xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
            <soap12:Header>
                <Authentication xmlns="http://xmlns.cenace.com/">
                <userNameToken>{userNameToken}</userNameToken>
                <passwordToken>{passwordToken}</passwordToken>
                <hd>{huellaDigital}</hd>
                </Authentication>
            </soap12:Header>
            <soap12:Body>
                <enviarOfertaCompraEnergia xmlns="http://xmlns.cenace.com/">
                <clvParticipante>{SOLARIO_KEY}</clvParticipante>
                <fechaInicial>{fechaInicial}</fechaInicial>
                <fechaFinal>{fechaInicial}</fechaFinal>
                <clvCarga>{elemento}</clvCarga>
                <clvSistema>{clvSistema}</clvSistema>
                <jsonOE>{bid_OE}</jsonOE>
                </enviarOfertaCompraEnergia>
            </soap12:Body>
            </soap12:Envelope>
            """
            #print(payload)
            response = requests.request('POST', URL_BID, headers=headers, data=payload)
            print(response.text)

            # RESETEAMOS PARA EL SIGUIENTE ELEMENTO
            bid_list = []
        else:
            bid_step = {
                "demandaFijaMw":df1['Oferta Ajustada'][i], # df1['Oferta(MWh)'][i]
                "hora":int(df1['Hora'][i])+1,
                "idSubInt":1,
                "oiMw01":0,
                "oiPrecio01":0,
                "oiMw02":0,
                "oiPrecio02":0,
                "oiMw03":0,
                "oiPrecio03":0,
            }
            bid_list.append(bid_step)