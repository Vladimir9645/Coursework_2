import sys

from api import SiteApi
from aeroplane import Aeroplane
from file_manager import JSONFileManager


def parse_aeroplanes(raw_states: list[list]) -> list[Aeroplane]:
    """Преобразует сырые данные OpenSky в список объектов Aeroplane.

    Индексы массива states (по документации OpenSky):
        [0]  icao24, [1] callsign, [2] origin_country,
        [5] longitude, [6] latitude, [7] altitude (barometric),
        [9] velocity, [8] on_ground
    """
    planes = []
    for state in raw_states:
        try:
            plane = Aeroplane(
                icao24=state[0],
                callsign=state[1],
                origin_country=state[2],
                longitude=state[5],
                latitude=state[6],
                altitude=state[7],
                velocity=state[9],
                on_ground=state[8] if len(state) > 8 else False,
            )
            planes.append(plane)
        except (ValueError, TypeError, IndexError):
            continue
    return planes


def show_top_by_altitude(planes: list[Aeroplane], n: int) -> None:
    """Выводит топ-N самолётов по высоте полёта."""
    sorted_planes = sorted(
        planes,
        key=lambda p: p.altitude if p.altitude is not None else -1,
        reverse=True,
    )
    print(f"\nТоп-{n} самолётов по высоте полёта:")
    print("-" * 80)
    for i, p in enumerate(sorted_planes[:n], 1):
        print(f"{i:>3}. {p}")
    print("-" * 80)


def show_by_country(planes: list[Aeroplane], country: str) -> None:
    """Выводит самолёты, зарегистрированные в указанной стране."""
    filtered = [p for p in planes if p.origin_country.lower() == country.lower()]
    if not filtered:
        print(f"\nСамолёты из страны '{country}' не найдены.")
        return
    print(f"\nСамолёты, зарегистрированные в стране '{country}' ({len(filtered)} шт.):")
    print("-" * 80)
    for i, p in enumerate(filtered, 1):
        print(f"{i:>3}. {p}")
    print("-" * 80)


def show_top_by_velocity(planes: list[Aeroplane], n: int) -> None:
    """Выводит топ-N самолётов по скорости полёта (доп. возможность)."""
    sorted_planes = sorted(
        planes,
        key=lambda p: p.velocity if p.velocity is not None else -1,
        reverse=True,
    )
    print(f"\nТоп-{n} самолётов по скорости полёта:")
    print("-" * 80)
    for i, p in enumerate(sorted_planes[:n], 1):
        print(f"{i:>3}. {p}")
    print("-" * 80)


def save_to_file(manager: JSONFileManager, planes: list[Aeroplane]) -> None:
    """Сохраняет самолёты в JSON-файл."""
    for p in planes:
        manager.add(p)
    print(f"\nСохранено {len(planes)} самолётов в файл {manager.filepath}")


def interactive_menu() -> None:
    """Главное меню взаимодействия с пользователем."""
    api = SiteApi()
    manager = JSONFileManager("aeroplanes.json")
    planes: list[Aeroplane] = []

    menu_text = """
╔══════════════════════════════════════════════╗
║   Отслеживание самолётов (OpenSky Network)   ║
╠══════════════════════════════════════════════╣
║  1. Запросить самолёты по стране             ║
║  2. Топ-N по высоте полёта                   ║
║  3. Самолёты по стране регистрации           ║
║  4. Топ-N по скорости полёта                 ║
║  5. Сохранить текущие данные в файл          ║
║  6. Загрузить данные из файла                ║
║  7. Показать общую статистику                ║
║  0. Выход                                    ║
╚══════════════════════════════════════════════╝
"""

    while True:
        print(menu_text)
        choice = input("Выберите действие: ").strip()

        if choice == "0":
            print("До свидания!")
            break

        elif choice == "1":
            country = input("Введите название страны (на английском): ").strip()
            if not country:
                print("Страна не указана.")
                continue
            try:
                print(f"Запрашиваю данные для страны: {country} ...")
                raw = api.get_aeroplane_data(country)
                planes = parse_aeroplanes(raw)
                print(f"Найдено самолётов: {len(planes)}")
                bbox = api.boundingbox
                print(f"Bounding box: {bbox}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "2":
            if not planes:
                print("Сначала запросите данные (пункт 1).")
                continue
            try:
                n = int(input("Введите N (сколько самолётов показать): "))
                if n <= 0:
                    print("N должно быть положительным.")
                    continue
            except ValueError:
                print("Некорректное число.")
                continue
            show_top_by_altitude(planes, n)

        elif choice == "3":
            if not planes:
                print("Сначала запросите данные (пункт 1).")
                continue
            country = input("Введите страну регистрации (на английском): ").strip()
            if not country:
                print("Страна не указана.")
                continue
            show_by_country(planes, country)

        elif choice == "4":
            if not planes:
                print("Сначала запросите данные (пункт 1).")
                continue
            try:
                n = int(input("Введите N: "))
                if n <= 0:
                    print("N должно быть положительным.")
                    continue
            except ValueError:
                print("Некорректное число.")
                continue
            show_top_by_velocity(planes, n)

        elif choice == "5":
            if not planes:
                print("Нет данных для сохранения.")
                continue
            save_to_file(manager, planes)

        elif choice == "6":
            loaded = manager.get_all()
            planes = loaded
            print(f"Загружено самолётов из файла: {len(loaded)}")

        elif choice == "7":
            if not planes:
                print("Нет данных. Сначала запросите (пункт 1).")
                continue
            total = len(planes)
            in_air = sum(1 for p in planes if not p.on_ground)
            on_ground = sum(1 for p in planes if p.on_ground)
            countries = set(p.origin_country for p in planes)
            avg_alt = (
                sum(p.altitude for p in planes if p.altitude is not None)
                / max(1, sum(1 for p in planes if p.altitude is not None))
            )
            avg_vel = (
                sum(p.velocity for p in planes if p.velocity is not None)
                / max(1, sum(1 for p in planes if p.velocity is not None))
            )
            print(f"\n--- Статистика ---")
            print(f"Всего самолётов:       {total}")
            print(f"В воздухе:             {in_air}")
            print(f"На земле:              {on_ground}")
            print(f"Стран регистрации:     {len(countries)}")
            print(f"Средняя высота:        {avg_alt:.1f} м")
            print(f"Средняя скорость:      {avg_vel:.1f} м/с")

        else:
            print("Неизвестная команда. Попробуйте снова.")


if __name__ == "__main__":
    interactive_menu()


