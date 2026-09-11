from __future__ import annotations


class Aeroplane:
    """Модель самолёта с валидацией и сравнением по скорости/высоте."""

    def __init__(
        self,
        icao24: str,
        callsign: str | None,
        origin_country: str,
        longitude: float | None,
        latitude: float | None,
        altitude: float | None,
        velocity: float | None,
        on_ground: bool = False,
    ) -> None:
        self._icao24 = self._validate_icao24(icao24)
        self._callsign = self._validate_callsign(callsign)
        self._origin_country = origin_country
        self._longitude = self._validate_coord(longitude, "longitude")
        self._latitude = self._validate_coord(latitude, "latitude")
        self._altitude = self._validate_numeric(altitude, "altitude")
        self._velocity = self._validate_numeric(velocity, "velocity")
        self._on_ground = bool(on_ground)

    # ── Валидация ──────────────────────────────────────────────

    @staticmethod
    def _validate_icao24(value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("icao24 должен быть непустой строкой.")
        return value.strip()

    @staticmethod
    def _validate_callsign(value: str | None) -> str:
        if value is None:
            return "N/A"
        return value.strip() if isinstance(value, str) else str(value)

    @staticmethod
    def _validate_coord(value: float | None, name: str) -> float | None:
        if value is None:
            return None
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} должен быть числом, получено {type(value)}.")
        return float(value)

    @staticmethod
    def _validate_numeric(value: float | None, name: str) -> float | None:
        if value is None:
            return None
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} должен быть числом, получено {type(value)}.")
        if value < 0:
            raise ValueError(f"{name} не может быть отрицательным.")
        return float(value)

    # ── Properties ─────────────────────────────────────────────

    @property
    def icao24(self) -> str:
        return self._icao24

    @property
    def callsign(self) -> str:
        return self._callsign

    @property
    def origin_country(self) -> str:
        return self._origin_country

    @property
    def longitude(self) -> float | None:
        return self._longitude

    @property
    def latitude(self) -> float | None:
        return self._latitude

    @property
    def altitude(self) -> float | None:
        return self._altitude

    @property
    def velocity(self) -> float | None:
        return self._velocity

    @property
    def on_ground(self) -> bool:
        return self._on_ground

    # ── Сравнения по скорости (операторы) ───────────────────────

    def __lt__(self, other: Aeroplane) -> bool:
        self._check_type(other)
        return self._cmp(self.velocity, other.velocity) < 0

    def __le__(self, other: Aeroplane) -> bool:
        self._check_type(other)
        return self._cmp(self.velocity, other.velocity) <= 0

    def __gt__(self, other: Aeroplane) -> bool:
        self._check_type(other)
        return self._cmp(self.velocity, other.velocity) > 0

    def __ge__(self, other: Aeroplane) -> bool:
        self._check_type(other)
        return self._cmp(self.velocity, other.velocity) >= 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._cmp(self.velocity, other.velocity) == 0

    # ── Сравнение по высоте (отдельные методы) ─────────────────

    def is_higher_than(self, other: Aeroplane) -> bool:
        self._check_type(other)
        return self._cmp(self.altitude, other.altitude) > 0

    def is_lower_than(self, other: Aeroplane) -> bool:
        self._check_type(other)
        return self._cmp(self.altitude, other.altitude) < 0

    # ── Вспомогательные ────────────────────────────────────────

    @staticmethod
    def _cmp(a: float | None, b: float | None) -> float:
        """Сравнивает два значения, None трактуется как 0."""
        a_val = a if a is not None else 0.0
        b_val = b if b is not None else 0.0
        return a_val - b_val

    @staticmethod
    def _check_type(other: object) -> None:
        if not isinstance(other, Aeroplane):
            raise TypeError("Сравнение возможно только с Aeroplane.")

    # ── Сериализация ────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "icao24": self._icao24,
            "callsign": self._callsign,
            "origin_country": self._origin_country,
            "longitude": self._longitude,
            "latitude": self._latitude,
            "altitude": self._altitude,
            "velocity": self._velocity,
            "on_ground": self._on_ground,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Aeroplane":
        return cls(
            icao24=data["icao24"],
            callsign=data.get("callsign"),
            origin_country=data["origin_country"],
            longitude=data.get("longitude"),
            latitude=data.get("latitude"),
            altitude=data.get("altitude"),
            velocity=data.get("velocity"),
            on_ground=data.get("on_ground", False),
        )

    def __repr__(self) -> str:
        return (
            f"Aeroplane(icao24={self._icao24!r}, callsign={self._callsign!r}, "
            f"origin_country={self._origin_country!r}, "
            f"altitude={self._altitude}, velocity={self._velocity})"
        )

    def __str__(self) -> str:
        return (
            f"  Позывной: {self._callsign} | ICAO: {self._icao24} | "
            f"Страна: {self._origin_country} | "
            f"Высота: {self._altitude} м | Скорость: {self._velocity} м/с"
        )
