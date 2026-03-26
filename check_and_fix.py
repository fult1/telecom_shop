import sqlite3


def check_and_fix():
    conn = sqlite3.connect('equipment.db')
    cursor = conn.cursor()

    # Проверяем наличие оборудования
    cursor.execute("SELECT COUNT(*) FROM equipment")
    count = cursor.fetchone()[0]

    print(f"Найдено записей в equipment: {count}")

    if count == 0:
        print("Нет данных! Добавляем...")

        # Добавляем тестовые данные
        test_data = [
            ('Маршрутизатор Cisco ISR 4321', 'Маршрутизаторы', 45000, 'Профессиональный маршрутизатор', 10),
            ('Коммутатор D-Link DGS-1210-28', 'Коммутаторы', 15000, 'Управляемый коммутатор', 15),
            ('Точка доступа Ubiquiti UniFi', 'Wi-Fi', 12000, 'Беспроводная точка доступа', 8),
            ('Сервер HP ProLiant DL380', 'Серверы', 120000, 'Сервер для ЦОД', 5),
            ('Медиаконвертер TP-Link', 'Медиаконвертеры', 3500, 'Gigabit Ethernet', 20),
        ]

        for data in test_data:
            cursor.execute('''
                INSERT INTO equipment (name, category, price, description, stock)
                VALUES (?, ?, ?, ?, ?)
            ''', data)

        conn.commit()
        print("Данные добавлены!")

    # Выводим все оборудование
    print("\nТекущий каталог:")
    cursor.execute("SELECT id, name, category, price, stock FROM equipment")
    for row in cursor.fetchall():
        print(f"  ID:{row[0]} | {row[1]} | {row[2]} | {row[3]} руб. | {row[4]} шт.")

    conn.close()


if __name__ == "__main__":
    check_and_fix()