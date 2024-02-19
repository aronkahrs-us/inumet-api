import requests
import datetime as dt
from unidecode import unidecode

BASE_URL = "https://www.inumet.gub.uy"

class INUMET:
    def __init__(self, station:str="", depto:str="") -> None:
        """
        Initialize the class.
        
        Parameters:
            station (str): Name of the weather station(from the self.estaciones() list).
            depto (str): Name of the state.
        """
        self._endpoints()
        self.depto = depto
        if station != "":
            self.station = [x['id'] for x in self.estaciones() if x['NombreEstacion'] == station][0]
        if depto != "":
            self.zone = [x['idInt'] for x in self.zonas() if unidecode(depto.lower().replace(" ","")) in x['deptos']][0]
        pass

    def estaciones(self) -> list:
        """
        Returns a list of Weather stations.
        """
        return self._request(self.endpoints['estaciones'])['estaciones']

    def zonas(self) -> list:
        """
        Returns a list of zones.
        """
        return self._request(self.endpoints['zonas'])['zonas']

    def departamentos(self) -> list:
        """
        Returns a list of states.
        """
        return self._request(self.endpoints['departamentos'])['deptos']

    def estado_actual(self) -> list:
        """
        Returns current weather conditions.
        If station is defined returns the current conditions for that specific station,
        else it returns current conditions of all available stations.
        """
        data = self._request(self.endpoints['estadoactual'])
        try:
            if self.station != "":
                if self.station in [x['id'] for x in data['estaciones']]:
                    return [x for x in data['estaciones'] if x['id'] == self.station ][0]
                else:
                    return self.get_estado()
            else:
                return data['estaciones']
        except:
            return data['estaciones']

    def pronostico(self) -> list:
        """
        Returns weather forecast.
        If zone is defined returns the current conditions for that specific station,
        else it returns current conditions of all available stations.
        If zone doesn't match any of the zones in self.zonas() it raises a ValueError.
        """
        forecast=[]
        data = self._request(self.endpoints['pronosticoV2'].replace('.mch','.json'))
        if self.zone != "" and self.zone in [x['idInt'] for x in self.zonas()['zonas']]:
            fechaInicio = data['inicioPronostico']
            #data=[x for x in data['items'] if x['zonaId'] == self.zone]
            for x in data['items']:
                 if x['zonaId'] == self.zone:
                    x['fecha'] = (dt.datetime.strptime(fechaInicio,'%Y-%m-%d') + dt.timedelta(days=x['diaMasN'])).isoformat()
                    estado = int(x['estadoTiempo'])
                    if estado == 4 or estado == 13 or estado == 24:
                        condition = 'cloudy'
                    elif estado == 12 or estado == 19:
                        condition = 'windy'
                    elif estado == 9 or estado == 2 or estado == 21 or estado == 22:
                        condition = 'partlycloudy'
                    elif estado == 1:
                        condition = 'sunny'
                    elif estado == 20:
                        condition = 'clear-night'
                    elif estado == 10:
                        condition = 'lightning'
                    elif estado == 11:
                        condition = 'lightning-rainy'
                    elif estado == 23 or estado == 3 or estado == 5 or estado == 6 or estado == 7:
                        condition = 'rainy'
                    elif estado == 16 or estado == 14 or estado == 15 or estado == 8:
                        condition = 'fog'
                    elif estado == 17:
                        condition = 'snowy'
                    elif estado == 18:
                        condition = 'exceptional'
                    x['condition']=condition
                    forecast.append(x)
            return forecast
        elif self.zone != "":
            raise ValueError
        else:
            return data['items']

    def advertencias(self) -> dict:
        """
        Returns weather alerts.
        """
        data = self._request(self.endpoints['nivelRiesgoV2'])
        return data

    def avisos(self) -> dict:
        """
        Returns weather information.
        """
        data = self._request("reportes/riesgo/avisoGral.mch")
        return data

    def _test(self) -> bool:
        """
        Test if all parmeters are correct and if station is working.
        """
        if self.station not in [x['id'] for x in self.estaciones()['estaciones']]:
            return False
        if self.depto not in [x['nombre'] for x in self.departamentos()['deptos']]:
            return False
        if self.zone not in [x['idInt'] for x in self.zonas()['zonas']]:
            return False
        if self.estado_actual() == False:
            return False
        return True

    def _get_data(self) -> dict:
        """
        Returns a dict with all relevant weather info (current conditions, forecast, alerts and info).
        """
        estado = self.estado_actual()
        pronostico = self.pronostico()
        advertencias = self.advertencias()
        avisos = self.avisos()
        return {"estado":estado,"pronostico":pronostico,"advertencias":advertencias,"avisos":avisos}

    def _pronostico_old(self):
        """
        Deprecated forecast
        """
        return self._request(self.endpoints['pronostico'])

    def _advertencias_old(self):
        """
        Deprecated alerts
        """
        return self._request(self.endpoints['nivelRiesgo'])

    def get_estado(self) -> dict:
        """
        Returns current weather conditions, mainly for automated weather stations.
        """
        data = self._request("reportes/estadoActual/datos_inumet_ui_publica.mch")
        estado = {
            "id": self.station,
            "dirViento": data['observaciones'][self._get_indice_id(data['variables'],8)]['datos'][self._get_indice_id(data['estaciones'],self.station)][0],
            "intViento": data['observaciones'][self._get_indice_id(data['variables'],29)]['datos'][self._get_indice_id(data['estaciones'],self.station)][0],
            "cielo": data['observaciones'][self._get_indice_id(data['variables'],3)]['datos'][self._get_indice_id(data['estaciones'],self.station)][0],
            "iconoTiempoPresente": data['observaciones'][self._get_indice_id(data['variables'],123)]['datos'][self._get_indice_id(data['estaciones'],self.station)][0],
            "visibilidad": data['observaciones'][self._get_indice_id(data['variables'],74)]['datos'][self._get_indice_id(data['estaciones'],self.station)][0],
            "temperatura": data['observaciones'][self._get_indice_id(data['variables'],47)]['datos'][self._get_indice_id(data['estaciones'],self.station)][0],
            "humedad": data['observaciones'][self._get_indice_id(data['variables'],25)]['datos'][self._get_indice_id(data['estaciones'],self.station)][0],
            "presion": data['observaciones'][self._get_indice_id(data['variables'],45)]['datos'][self._get_indice_id(data['estaciones'],self.station)][0],
        }
        nodata=[estado[x] for x in estado]
        if nodata.count(None) > len(estado)-6:
            return False
        else:
            return estado

    def _get_indice_id(self, coleccion, id) -> int:
        """
        Returns if of specific data.
        """
        encontre = False
        indice_id = -1
        if id != "":
            for i in range(len(coleccion)):
                if not encontre and (coleccion[i].get('id') == id or coleccion[i].get('idInt') == id):
                    encontre = True
                    indice_id = i
        return indice_id

    def _endpoints(self) -> dict:
        """
        Returns dict of endpoints.
        """
        self.endpoints = {x['nombre']: x['url'] for x in self._request("/android/info_recursosV5.json")['info_recursos']}
        return self.endpoints

    def _request(self,path:str):
        """
        Make the request to the server.
        """
        return requests.get(url=f"{BASE_URL}/{path}").json()