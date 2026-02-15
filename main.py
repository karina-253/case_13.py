import datetime
import math
import random
import local as lcl


def get_information(initial_data):
    """
    Function for reading information from a file and creating a dictionary with automates.
    :param initial_data: Path to the file containing automate data.
    :return: A dictionary where keys are automate numbers and values are dictionaries containing
    maximum queue length, brands, current queue length, and the end time of the previous client.
    """
    automates = {}
    with open(initial_data, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():
                parts = line.strip().split()
                num = int(parts[0])
                max_queue = int(parts[1])
                brands = parts[2:]
                automates[num] = {
                    'max_queue': max_queue,
                    'brands': brands,
                    'queue': 0,
                    'previous_time': datetime.datetime.strptime('00:00', '%H:%M'),
                    'current_client': None  # Текущий обслуживаемый клиент
                }
    return automates


def get_request(line):
    """
    Function changes the request line to the dictionary.
    :param line: A string containing time, volume, and brand information.
    :return: A dictionary with keys 'time', 'volume', and 'brand'.
    """
    time_str, volume, brand = line.strip().split()
    return {
        'time': datetime.datetime.strptime(time_str, '%H:%M'),
        'volume': int(volume),
        'brand': brand
    }


def suitable_automates(request, automates):
    """
    Function searches for a suitable automate that support the requested brand.
    :param request: A dictionary containing the request details.
    :param automates: A dictionary containing automate data.
    :return: A dictionary of suitable automates.
    """
    return {num: automates[num] for num in automates
            if request['brand'] in automates[num]['brands']}


def automate_num(suitable):
    """
    Selects automate with the shortest queue that is below its maximum capacity.
    :param suitable: A dictionary of suitable automates.
    :return: The number of the selected automate.
    """
    if not suitable:
        return 0

    # Находим автомат с наименьшей очередью, которая не достигла максимума
    available = {num: data for num, data in suitable.items()
                 if data['queue'] < data['max_queue']}

    if not available:
        return 0

    # Выбираем автомат с наименьшей очередью
    return min(available.keys(), key=lambda x: available[x]['queue'])


def refuel_time(volume):
    """
    Function calculating refueling time based on the requested volume.
    :param volume: The volume of fuel.
    :return: The calculated refueling time in minutes.
    """
    # Базовая длительность (округляем вверх)
    base_time = math.ceil(volume / 10)
    # Случайная вариация
    variation = random.choice([-1, 0, 1])
    # Гарантируем, что время не станет 0 или отрицательным
    return max(1, base_time + variation)


def print_automates_state(automates):
    """
    Prints the current state of all automates.
    """
    for num in sorted(automates.keys()):
        automate = automates[num]
        queue_display = '*' * automate['queue']
        print(f'{lcl.AUTOMATE_NUMBER}{num} {lcl.MAX_QUEUE_LENGTH}: {automate["max_queue"]} '
              f'{lcl.GASOLINE_BRANDS}: {" ".join(automate["brands"])} '
              f'->{queue_display}')


def calculate_lost_profit(gas_prices, fuel_sold_by_brand, lost_clients_by_brand):
    """
    Calculates and analyzes lost profit and recommends a new fuel column.
    """
    print(f"\n{'=' * 60}")
    print("АНАЛИЗ РЕНТАБЕЛЬНОСТИ ДОПОЛНИТЕЛЬНОЙ КОЛОНКИ")
    print(f"{'=' * 60}")

    # Статистика по потерянным клиентам
    print("\nПотерянные клиенты по маркам топлива:")
    total_lost_volume = 0
    total_lost_revenue = 0

    for brand in sorted(gas_prices.keys()):
        lost_count = lost_clients_by_brand.get(brand, 0)
        if lost_count > 0:
            # Оцениваем средний объем для потерянных клиентов (используем средний объем проданного топлива)
            if fuel_sold_by_brand[brand] > 0:
                avg_volume = fuel_sold_by_brand[brand] / max(1, sum(fuel_sold_by_brand.values()))
            else:
                avg_volume = 30  # Средний объем, если нет данных

            lost_volume = lost_count * avg_volume
            lost_revenue = lost_volume * gas_prices[brand]

            total_lost_volume += lost_volume
            total_lost_revenue += lost_revenue

            print(f"  {brand}: {lost_count} клиентов, "
                  f"потеряно ~{lost_volume:.1f} л, "
                  f"упущенная выручка ~{lost_revenue:.2f} руб.")

    print(f"\nИТОГО: потеряно {total_lost_volume:.1f} л, "
          f"упущенная выручка {total_lost_revenue:.2f} руб.")

    # Анализ необходимости новой колонки
    print(f"\nАНАЛИЗ НЕОБХОДИМОСТИ НОВОЙ КОЛОНКИ:")

    # Находим марку с наибольшими потерями
    if lost_clients_by_brand:
        most_lost_brand = max(lost_clients_by_brand.items(),
                              key=lambda x: x[1])[0]

        print(f"Наибольшее количество потерянных клиентов - марка {most_lost_brand}")
        print(f"Рекомендуется установить дополнительную колонку с топливом {most_lost_brand}")

        # Оценка рентабельности
        monthly_lost_revenue = total_lost_revenue * 30  # Приблизительно за месяц
        column_cost = 1500000  # Примерная стоимость колонки в рублях
        months_to_payback = column_cost / monthly_lost_revenue if monthly_lost_revenue > 0 else float('inf')

        print(f"\nОЦЕНКА РЕНТАБЕЛЬНОСТИ:")
        print(f"Ежемесячная упущенная выгода (приблизительно): {monthly_lost_revenue:,.0f} руб.")
        print(f"Примерная стоимость новой колонки: {column_cost:,.0f} руб.")

        if months_to_payback <= 12:
            print(f"Срок окупаемости: {months_to_payback:.1f} месяцев (РЕНТАБЕЛЬНО)")
        elif months_to_payback <= 24:
            print(f"Срок окупаемости: {months_to_payback:.1f} месяцев (УМЕРЕННО РЕНТАБЕЛЬНО)")
        else:
            print(f"Срок окупаемости: {months_to_payback:.1f} месяцев (НЕРЕНТАБЕЛЬНО)")
    else:
        print("Потерянных клиентов нет - дополнительная колонка не требуется")


def main():
    """
    Main function
    :return: None
    """
    # Цены на бензин
    gas_prices = {'АИ-80': 45.0, 'АИ-92': 50.5, 'АИ-95': 54.8, 'АИ-98': 62.3}

    # Статистика продаж
    fuel_sold = {'АИ-80': 0, 'АИ-92': 0, 'АИ-95': 0, 'АИ-98': 0}
    total_revenue = 0
    lost_clients = 0
    lost_clients_by_brand = {'АИ-80': 0, 'АИ-92': 0, 'АИ-95': 0, 'АИ-98': 0}

    # Чтение данных об автоматах
    automates = get_information('azs.txt')

    # Словарь для хранения событий завершения обслуживания
    # Ключ - время завершения, значение - информация о клиенте
    finish_events = {}

    # Чтение и обработка запросов
    with open('input.txt', 'r', encoding='utf-8') as requests_file:
        all_requests = [get_request(line) for line in requests_file if line.strip()]

    # Сортируем запросы по времени
    all_requests.sort(key=lambda x: x['time'])

    # Обработка каждого запроса
    for request in all_requests:
        current_time = request['time']

        # Обрабатываем все события завершения, которые произошли до текущего времени
        while finish_events and min(finish_events.keys()) <= current_time:
            finish_time = min(finish_events.keys())
            finish_info = finish_events[finish_time]

            # Выводим информацию о завершении заправки
            print(f'\nВ {finish_time.strftime("%H:%M")} клиент {finish_info["arrival_time"].strftime("%H:%M")} '
                  f'{finish_info["brand"]} {finish_info["volume"]} {finish_info["duration"]} '
                  f'{lcl.FINISHED_REFUELING}')

            # Освобождаем автомат
            automate = automates[finish_info['num']]
            automate['queue'] -= 1
            automate['previous_time'] = finish_time
            automate['current_client'] = None

            # Удаляем событие
            del finish_events[finish_time]

            # Выводим состояние автоматов
            print_automates_state(automates)

        # Обработка нового клиента
        suitable = suitable_automates(request, automates)
        chosen_num = automate_num(suitable)

        if not chosen_num:
            lost_clients += 1
            lost_clients_by_brand[request['brand']] += 1
            print(f'\nВ {request["time"].strftime("%H:%M")} {lcl.CLIENT_LEFT} {request["brand"]} '
                  f'{lcl.CLIENT_LEFT_STATION}')
            print_automates_state(automates)
        else:
            # Расчет времени обслуживания
            duration = refuel_time(request['volume'])

            # Добавляем клиента в очередь
            automates[chosen_num]['queue'] += 1

            # Выводим информацию о постановке в очередь
            print(f'\nВ {request["time"].strftime("%H:%M")} {lcl.NEW_CLIENT}: '
                  f'{request["time"].strftime("%H:%M")} {request["brand"]} {request["volume"]} {duration} '
                  f'{lcl.CLIENT_QUEUED}{chosen_num}')

            print_automates_state(automates)

            # Планируем завершение обслуживания
            previous_finish = automates[chosen_num]['previous_time']
            start_time = max(previous_finish, request['time'])
            finish_time = start_time + datetime.timedelta(minutes=duration)

            finish_events[finish_time] = {
                'num': chosen_num,
                'arrival_time': request['time'],
                'brand': request['brand'],
                'volume': request['volume'],
                'duration': duration
            }

            # Обновляем статистику продаж
            fuel_sold[request['brand']] += request['volume']
            total_revenue += request['volume'] * gas_prices[request['brand']]

    # Обрабатываем оставшиеся события завершения
    while finish_events:
        finish_time = min(finish_events.keys())
        finish_info = finish_events[finish_time]

        print(f'\nВ {finish_time.strftime("%H:%M")} клиент {finish_info["arrival_time"].strftime("%H:%M")} '
              f'{finish_info["brand"]} {finish_info["volume"]} {finish_info["duration"]} '
              f'{lcl.FINISHED_REFUELING}')

        automates[finish_info['num']]['queue'] -= 1
        automates[finish_info['num']]['previous_time'] = finish_time
        automates[finish_info['num']]['current_client'] = None

        del finish_events[finish_time]

        print_automates_state(automates)

    # Вывод итоговой статистики
    print(f'\n{"=" * 60}')
    print(f'{lcl.GASOLINE_SOLD}:')
    for brand in sorted(fuel_sold.keys()):
        print(f'  {brand}: {fuel_sold[brand]} л')

    print(f'\n{lcl.GASOLINE_SOLD_FINALL}: {sum(fuel_sold.values())} л')
    print(f'{lcl.REVENUE}: {total_revenue:.2f} руб.')
    print(f'{lcl.LOST_CLIENTS}: {lost_clients}')

    # Анализ рентабельности дополнительной колонки
    calculate_lost_profit(gas_prices, fuel_sold, lost_clients_by_brand)


if __name__ == '__main__':
    main()
