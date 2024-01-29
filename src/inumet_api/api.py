import requests

BASE_URL = "https://www.inumet.gub.uy"

class INUMET:
    def __init__(self,zone:int=None, station:int=None) -> None:
        self.zone = zone
        self.station = station
        self._endpoints()
        pass

    def estaciones(self):
        return self._request(self.endpoints['estaciones'])

    def zonas(self):
        return self._request(self.endpoints['zonas'])

    def departamentos(self):
        return self._request(self.endpoints['departamentos'])

    def estado_actual(self):
        data = self._request(self.endpoints['estadoactual'])
        date = data['Fecha']
        time = data['Hora']
        if self.station:
            return [x for x in data['estaciones'] if x['estacion'] == self.station ][0]
        else:
            return data['estaciones']

    def pronostico(self):
        data = self._request(self.endpoints['pronosticoV2'].replace('.mch','.json'))
        if self.zone and self.zone in [x['idInt'] for x in self.zonas()['zonas']]:
            data=[x for x in data['items'] if x['zonaId'] == self.zone]
            return data
        elif self.zone:
            raise ValueError
        else:
            return data['items']

    def advertencias(self):
        data=self._request(self.endpoints['nivelRiesgoV2'])
        pronosticador = data['pronosticador']
        advertencias = data['advertencias']
        actualizacion = data['fechaActualizacion']
        mapa = data['mapaMerge']
        return pronosticador,advertencias,actualizacion,mapa
    
    def _test(self):
        if self.station not in [x['id'] for x in self.estaciones()['estaciones']]:
            raise ValueError
        if self.zone not in [x['idInt'] for x in self.zonas()['zonas']]:
            raise ValueError
        return True


    def _pronostico_old(self):
        return self._request(self.endpoints['pronostico'])

    def _advertencias_old(self):
        return self._request(self.endpoints['nivelRiesgo'])

    def _endpoints(self):
        self.endpoints = {x['nombre']: x['url'] for x in self._request("/android/info_recursosV5.json")['info_recursos']}
        return self.endpoints

    def _request(self,path:str):
        return requests.get(url=f"{BASE_URL}/{path}").json()