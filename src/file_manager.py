from abc import ABC, abstractmethod
import csv
import json
import os
from typing import Any

from aeroplane import Aeroplane


class FileManagerInterface(ABC):
    """Абстрактный класс для работы с хранилищем данных о самолётах.

    Заглушки методов, которые не нужны для файлового хранилища,
    но пригодятся при переходе на БД, помечены как NotImplementedError.
    """

    @abstractmethod
    def add(self, aeroplane: Aeroplane) -> None:
        """Добавляет информацию о самолёте в хранилище."""
        pass

    @abstractmethod
    def get_by_criteria(self, criteria: dict) -> list[Aeroplane]:
        """Получает самолёты по указанным критериям."""
        pass

    @abstractmethod
    def delete(self, criteria: dict) -> int:
        """Удаляет самолёты по критериям. Возвращает количество удалённых."""
        pass

    @abstractmethod
    def get_all(self) -> list[Aeroplane]:
        """Возвращает все самолёты из хранилища."""
        pass

    # ── Заглушки для будущей интеграции с БД ────────────────────

    def connect(self, *args: Any, **kwargs: Any) -> None:
        """Подключение к хранилищу (для БД)."""
        raise NotImplementedError("Метод не требуется для файлового хранилища.")

    def disconnect(self) -> None:
        """Отключение от хранилища (для БД)."""
        raise NotImplementedError("Метод не требуется для файлового хранилища.")


class JSONFileManager(FileManagerInterface):
    """Сохранение и чтение данных о самолётах в JSON-файл."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Создаёт файл, если он не существует."""
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read_raw(self) -> list[dict]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_raw(self, data: list[dict]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, aeroplane: Aeroplane) -> None:
        data = self._read_raw()
        data.append(aeroplane.to_dict())
        self._write_raw(data)

    def get_by_criteria(self, criteria: dict) -> list[Aeroplane]:
        data = self._read_raw()
        result = []
        for record in data:
            if all(record.get(key) == value for key, value in criteria.items()):
                result.append(Aeroplane.from_dict(record))
        return result

    def delete(self, criteria: dict) -> int:
        data = self._read_raw()
        kept = []
        removed = 0
        for record in data:
            if all(record.get(key) == value for key, value in criteria.items()):
                removed += 1
            else:
                kept.append(record)
        self._write_raw(kept)
        return removed

    def get_all(self) -> list[Aeroplane]:
        return [Aeroplane.from_dict(r) for r in self._read_raw()]


class CSVFileManager(FileManagerInterface):
    """Сохранение и чтение данных о самолётах в CSV-файл."""

    FIELDS = [
        "icao24", "callsign", "origin_country",
        "longitude", "latitude", "altitude",
        "velocity", "on_ground",
    ]

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDS)
                writer.writeheader()

    def add(self, aeroplane: Aeroplane) -> None:
        with open(self.filepath, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDS)
            writer.writerow(aeroplane.to_dict())

    def get_all(self) -> list[Aeroplane]:
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            planes = []
            for row in reader:
                # Преобразуем типы
                row["longitude"] = float(row["longitude"]) if row["longitude"] not in ("", "None") else None
                row["latitude"] = float(row["latitude"]) if row["latitude"] not in ("", "None") else None
                row["altitude"] = float(row["altitude"]) if row["altitude"] not in ("", "None") else None
                row["velocity"] = float(row["velocity"]) if row["velocity"] not in ("", "None") else None
                row["on_ground"] = row["on_ground"] == "True"
                planes.append(Aeroplane.from_dict(row))
            return planes

    def get_by_criteria(self, criteria: dict) -> list[Aeroplane]:
        all_planes = self.get_all()
        return [
            p for p in all_planes
            if all(getattr(p, key, None) == value for key, value in criteria.items())
        ]

    def delete(self, criteria: dict) -> int:
        all_planes = self.get_all()
        kept = []
        removed = 0
        for p in all_planes:
            if all(getattr(p, key, None) == value for key, value in criteria.items()):
                removed += 1
            else:
                kept.append(p)
        # Перезаписываем файл
        with open(self.filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDS)
            writer.writeheader()
            for p in kept:
                writer.writerow(p.to_dict())
        return removed
