import sqlite3
import hashlib


class Database:
    def __init__(self, db_name='equipment.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        ''')

        # Таблица оборудования
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                stock INTEGER DEFAULT 0
            )
        ''')

        # Таблица заказов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                equipment_id INTEGER,
                quantity INTEGER,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (equipment_id) REFERENCES equipment(id)
            )
        ''')

        # Добавляем тестовые данные
        self.add_test_data()
        self.conn.commit()

    def add_test_data(self):
        # Добавляем администратора
        admin_pass = hashlib.sha256('admin123'.encode()).hexdigest()
        self.cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, is_admin)
            VALUES (?, ?, ?)
        ''', ('admin', admin_pass, 1))

        # Добавляем тестовое оборудование
        test_equipment = [
            ('Маршрутизатор Cisco ISR 4321', 'Маршрутизаторы', 45000, 'Профессиональный маршрутизатор для предприятий',
             10),
            ('Коммутатор D-Link DGS-1210-28', 'Коммутаторы', 15000, 'Управляемый коммутатор 28 портов', 15),
            ('Точка доступа Ubiquiti UniFi U6-LR', 'Wi-Fi', 12000, 'Беспроводная точка доступа Wi-Fi 6', 8),
            ('Медиаконвертер TP-Link MC220L', 'Медиаконвертеры', 3500, 'Gigabit Ethernet медиаконвертер', 20),
            ('Сервер HP ProLiant DL380 Gen10', 'Серверы', 120000, 'Сервер для центров обработки данных', 5),
        ]

        for eq in test_equipment:
            self.cursor.execute('''
                INSERT OR IGNORE INTO equipment (name, category, price, description, stock)
                VALUES (?, ?, ?, ?, ?)
            ''', eq)

        self.conn.commit()

    def authenticate(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute('''
            SELECT id, username, is_admin FROM users 
            WHERE username = ? AND password = ?
        ''', (username, password_hash))
        return self.cursor.fetchone()

    def register_user(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password, is_admin)
                VALUES (?, ?, ?)
            ''', (username, password_hash, 0))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_equipment(self, category=None):
        """Получение списка оборудования"""
        try:
            if category and category != 'Все' and category is not None:
                self.cursor.execute('''
                    SELECT * FROM equipment WHERE category = ? AND stock > 0
                    ORDER BY category, name
                ''', (category,))
            else:
                self.cursor.execute('''
                    SELECT * FROM equipment WHERE stock > 0
                    ORDER BY category, name
                ''')

            equipment = self.cursor.fetchall()
            print(f"Загружено {len(equipment)} позиций оборудования")  # Отладочное сообщение
            return equipment
        except Exception as e:
            print(f"Ошибка при загрузке оборудования: {e}")
            return []

    def get_categories(self):
        self.cursor.execute('SELECT DISTINCT category FROM equipment')
        return [row[0] for row in self.cursor.fetchall()]

    def create_order(self, user_id, equipment_id, quantity):
        # Проверяем наличие на складе
        self.cursor.execute('SELECT stock FROM equipment WHERE id = ?', (equipment_id,))
        stock = self.cursor.fetchone()[0]

        if stock >= quantity:
            self.cursor.execute('''
                INSERT INTO orders (user_id, equipment_id, quantity)
                VALUES (?, ?, ?)
            ''', (user_id, equipment_id, quantity))

            # Обновляем количество на складе
            self.cursor.execute('''
                UPDATE equipment SET stock = stock - ? WHERE id = ?
            ''', (quantity, equipment_id))

            self.conn.commit()
            return True
        return False

    def get_orders(self, user_id=None):
        if user_id:
            self.cursor.execute('''
                SELECT o.id, e.name, o.quantity, o.order_date, o.status
                FROM orders o
                JOIN equipment e ON o.equipment_id = e.id
                WHERE o.user_id = ?
                ORDER BY o.order_date DESC
            ''', (user_id,))
        else:
            self.cursor.execute('''
                SELECT o.id, u.username, e.name, o.quantity, o.order_date, o.status
                FROM orders o
                JOIN users u ON o.user_id = u.id
                JOIN equipment e ON o.equipment_id = e.id
                ORDER BY o.order_date DESC
            ''')
        return self.cursor.fetchall()

    def update_order_status(self, order_id, status):
        self.cursor.execute('''
            UPDATE orders SET status = ? WHERE id = ?
        ''', (status, order_id))
        self.conn.commit()

    def add_equipment(self, name, category, price, description, stock):
        self.cursor.execute('''
            INSERT INTO equipment (name, category, price, description, stock)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, category, price, description, stock))
        self.conn.commit()

    def delete_equipment(self, equipment_id):
        self.cursor.execute('DELETE FROM equipment WHERE id = ?', (equipment_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()