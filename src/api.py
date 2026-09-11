from abc import ABC, abstractmethod
from typing import Any

import requests


class SiteApiInterface(ABC):
    """Абстрактный класс для работы с внешними API."""

    @abstractmethod
    def get_page_data(self, response: requests.Response) -> Any:
        """Извлекает данные из ответа API."""
        pass

    @abstractmethod
    def _get_response(self, url: str, params: dict | None = None) -> requests.Response:
        """Выполняет HTTP-запрос и возвращает ответ."""
        pass


class SiteApi(SiteApiInterface):
    """Работа с API Nominatim и OpenSky Network."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"

    def __init__(self) -> None:
        self.aeroplanes: list[list] = []
        self.boundingbox: list[str] = []

    def _get_response(self, url: str, params: dict | None = None) -> requests.Response:
        headers = {
            "User-Agent": "CourseWorkAeroplanes/1.0",
            "Accept": "application/json",
        }
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response

    def get_page_data(self, response: requests.Response) -> Any:
        return response.json()

    def get_country_coordinates(self, country: str) -> list[str]:
        """Получает bounding box страны через Nominatim API."""
        params = {"country": country, "format": "json", "limit": 1}
        response = self._get_response(self.NOMINATIM_URL, params)
        data = self.get_page_data(response)

        if not data:
            raise ValueError(f"Страна '{country}' не найдена в Nominatim.")

        self.boundingbox = data[0]["boundingbox"]
        return self.boundingbox

    def get_aeroplane_data(self, country: str) -> list[list]:
        """Получает данные о самолётах в воздушном пространстве страны.

        Сначала запрашивает bounding box через Nominatim,
        затем — самолёты в этом периметре через OpenSky.
        """
        bbox = self.get_country_coordinates(country)
        south_lat, north_lat, west_lon, east_lon = bbox

        params = {
            "lamin": float(south_lat),
            "lamax": float(north_lat),
            "lomin": float(west_lon),
            "lomax": float(east_lon),
        }

        response = self._get_response(self.OPENSKY_URL, params)
        data = self.get_page_data(response)

        self.aeroplanes = data.get("states") or []
        return self.aeroplanes

