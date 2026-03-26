import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class UserPanel:
    def __init__(self, parent, db, user_id, username):
        self.parent = parent
        self.db = db
        self.user_id = user_id
        self.username = username

        self.window = tk.Toplevel(parent)
        self.window.title(f"Каталог оборудования - {username}")
        self.window.geometry("1000x600")  # Увеличил размер окна

        self.create_widgets()
        self.load_equipment()

    def create_widgets(self):
        # Верхняя панель
        top_frame = tk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(top_frame, text=f"Пользователь: {self.username}",
                 font=("Arial", 12)).pack(side=tk.LEFT)

        tk.Button(top_frame, text="Мои заказы", command=self.show_orders,
                  bg="#4CAF50", fg="white").pack(side=tk.RIGHT, padx=5)

        # Панель фильтрации
        filter_frame = tk.LabelFrame(self.window, text="Фильтр", padx=10, pady=5)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Категория:").pack(side=tk.LEFT, padx=5)

        self.category_var = tk.StringVar(value="Все")
        categories = ["Все"] + self.db.get_categories()
        self.category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var,
                                           values=categories, width=20)
        self.category_combo.pack(side=tk.LEFT, padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self.load_equipment())

        # Создаем фрейм для таблицы и скролла
        table_frame = tk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Таблица оборудования
        columns = ('ID', 'Название', 'Категория', 'Цена', 'Наличие', 'Описание')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Настройка колонок
        self.tree.heading('ID', text='ID')
        self.tree.heading('Название', text='Название')
        self.tree.heading('Категория', text='Категория')
        self.tree.heading('Цена', text='Цена')
        self.tree.heading('Наличие', text='Наличие')
        self.tree.heading('Описание', text='Описание')

        self.tree.column('ID', width=50)
        self.tree.column('Название', width=250)
        self.tree.column('Категория', width=120)
        self.tree.column('Цена', width=100)
        self.tree.column('Наличие', width=80)
        self.tree.column('Описание', width=300)

        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Размещение таблицы и скролла
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Панель заказа
        order_frame = tk.LabelFrame(self.window, text="Оформление заказа", padx=10, pady=5)
        order_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(order_frame, text="Выберите товар и укажите количество:").pack(side=tk.LEFT, padx=5)

        tk.Label(order_frame, text="Количество:").pack(side=tk.LEFT, padx=5)
        self.quantity_entry = tk.Entry(order_frame, width=10)
        self.quantity_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(order_frame, text="Заказать", command=self.make_order,
                  bg="#2196F3", fg="white", width=15).pack(side=tk.LEFT, padx=10)

        # Информационная метка
        self.info_label = tk.Label(self.window, text="", fg="blue")
        self.info_label.pack(pady=5)

    def load_equipment(self):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        category = self.category_var.get()
        if category == "Все":
            equipment = self.db.get_equipment(None)
        else:
            equipment = self.db.get_equipment(category)

        if not equipment:
            self.info_label.config(text="В каталоге пока нет оборудования. Обратитесь к администратору.", fg="red")
            return
        else:
            self.info_label.config(text=f"Найдено {len(equipment)} позиций", fg="green")

        for eq in equipment:
            values = (
                eq[0],  # ID
                eq[1],  # Название
                eq[2],  # Категория
                f"{eq[3]:.2f} руб.",  # Цена
                f"{eq[5]} шт.",  # Наличие
                eq[4]  # Описание
            )
            self.tree.insert('', tk.END, values=values)

    def make_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите оборудование для заказа")
            return

        item = self.tree.item(selected[0])
        equipment_id = item['values'][0]
        equipment_name = item['values'][1]

        # Получаем количество из строки "X шт."
        stock_text = item['values'][4]
        stock = int(stock_text.split()[0])

        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError
            if quantity > stock:
                messagebox.showerror("Ошибка", f"Недостаточно товара. В наличии только {stock} шт.")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество (целое положительное число)")
            return

        if self.db.create_order(self.user_id, equipment_id, quantity):
            messagebox.showinfo("Успех", f"Заказ на '{equipment_name}' в количестве {quantity} шт. оформлен!")
            self.quantity_entry.delete(0, tk.END)
            self.load_equipment()  # Обновляем список
        else:
            messagebox.showerror("Ошибка", "Не удалось оформить заказ. Возможно, товар закончился.")

    def show_orders(self):
        orders_window = tk.Toplevel(self.window)
        orders_window.title("Мои заказы")
        orders_window.geometry("800x500")

        # Создаем фрейм для таблицы
        frame = tk.Frame(orders_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('ID', 'Товар', 'Количество', 'Дата', 'Статус')
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)

        # Настройка колонок
        tree.heading('ID', text='№ заказа')
        tree.heading('Товар', text='Товар')
        tree.heading('Количество', text='Количество')
        tree.heading('Дата', text='Дата заказа')
        tree.heading('Статус', text='Статус')

        tree.column('ID', width=80)
        tree.column('Товар', width=300)
        tree.column('Количество', width=80)
        tree.column('Дата', width=150)
        tree.column('Статус', width=100)

        # Скроллбар
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Загружаем заказы
        orders = self.db.get_orders(self.user_id)

        if not orders:
            # Показываем сообщение
            label = tk.Label(orders_window, text="У вас пока нет заказов", font=("Arial", 12), fg="gray")
            label.pack(pady=50)
        else:
            for order in orders:
                status_text = "✅ Выполнен" if order[4] == 'completed' else "⏳ Ожидает"
                if order[4] == 'cancelled':
                    status_text = "❌ Отменен"

                tree.insert('', tk.END, values=(
                    order[0],  # ID
                    order[1],  # Товар
                    f"{order[2]} шт.",  # Количество
                    order[3],  # Дата
                    status_text  # Статус
                ))

        # Кнопка закрытия
        tk.Button(orders_window, text="Закрыть", command=orders_window.destroy,
                  bg="#f44336", fg="white", width=15).pack(pady=10)