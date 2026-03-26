import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class AdminPanel:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db

        self.window = tk.Toplevel(parent)
        self.window.title("Администраторская панель")
        self.window.geometry("1000x700")

        self.create_widgets()
        self.load_orders()

    def create_widgets(self):
        # Вкладки
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка заказов
        orders_frame = tk.Frame(self.notebook)
        self.notebook.add(orders_frame, text="Заказы")
        self.create_orders_tab(orders_frame)

        # Вкладка управления оборудованием
        equipment_frame = tk.Frame(self.notebook)
        self.notebook.add(equipment_frame, text="Управление оборудованием")
        self.create_equipment_tab(equipment_frame)

    def create_orders_tab(self, parent):
        # Таблица заказов
        columns = ('ID', 'Пользователь', 'Товар', 'Количество', 'Дата', 'Статус', 'Действие')
        self.orders_tree = ttk.Treeview(parent, columns=columns, show='headings', height=20)

        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=100)

        self.orders_tree.column('Пользователь', width=150)
        self.orders_tree.column('Товар', width=200)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        tk.Button(button_frame, text="Подтвердить заказ", command=self.approve_order,
                  bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Отменить заказ", command=self.cancel_order,
                  bg="#f44336", fg="white").pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Обновить", command=self.load_orders,
                  bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)

    def create_equipment_tab(self, parent):
        # Форма добавления оборудования
        add_frame = tk.LabelFrame(parent, text="Добавить оборудование", padx=10, pady=10)
        add_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(add_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = tk.Entry(add_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5)

        tk.Label(add_frame, text="Категория:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_entry = tk.Entry(add_frame, width=30)
        self.category_entry.grid(row=1, column=1, pady=5)

        tk.Label(add_frame, text="Цена:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.price_entry = tk.Entry(add_frame, width=30)
        self.price_entry.grid(row=2, column=1, pady=5)

        tk.Label(add_frame, text="Описание:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.desc_entry = tk.Entry(add_frame, width=30)
        self.desc_entry.grid(row=3, column=1, pady=5)

        tk.Label(add_frame, text="Количество:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.stock_entry = tk.Entry(add_frame, width=30)
        self.stock_entry.grid(row=4, column=1, pady=5)

        tk.Button(add_frame, text="Добавить", command=self.add_equipment,
                  bg="#4CAF50", fg="white").grid(row=5, column=1, pady=10)

        # Таблица оборудования
        columns = ('ID', 'Название', 'Категория', 'Цена', 'Наличие')
        self.equip_tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)

        for col in columns:
            self.equip_tree.heading(col, text=col)
            self.equip_tree.column(col, width=100)

        self.equip_tree.column('Название', width=250)
        self.equip_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Button(parent, text="Удалить выбранное", command=self.delete_equipment,
                  bg="#f44336", fg="white").pack(pady=5)

        self.load_equipment()

    def load_orders(self):
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        orders = self.db.get_orders()

        for order in orders:
            status_text = "Ожидает" if order[5] == 'pending' else "Выполнен"
            values = (order[0], order[1], order[2], order[3], order[4], status_text)
            self.orders_tree.insert('', tk.END, values=values)

    def load_equipment(self):
        for item in self.equip_tree.get_children():
            self.equip_tree.delete(item)

        equipment = self.db.get_equipment()

        for eq in equipment:
            values = (eq[0], eq[1], eq[2], f"{eq[3]:.2f} руб.", eq[5])
            self.equip_tree.insert('', tk.END, values=values)

    def approve_order(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ")
            return

        item = self.orders_tree.item(selected[0])
        order_id = item['values'][0]

        self.db.update_order_status(order_id, 'completed')
        messagebox.showinfo("Успех", f"Заказ №{order_id} подтвержден")
        self.load_orders()

    def cancel_order(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ")
            return

        item = self.orders_tree.item(selected[0])
        order_id = item['values'][0]

        self.db.update_order_status(order_id, 'cancelled')
        messagebox.showinfo("Успех", f"Заказ №{order_id} отменен")
        self.load_orders()

    def add_equipment(self):
        name = self.name_entry.get()
        category = self.category_entry.get()
        price = self.price_entry.get()
        description = self.desc_entry.get()
        stock = self.stock_entry.get()

        if not all([name, category, price, stock]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            messagebox.showerror("Ошибка", "Цена и количество должны быть числами")
            return

        self.db.add_equipment(name, category, price, description, stock)
        messagebox.showinfo("Успех", "Оборудование добавлено")

        # Очищаем поля
        self.name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)

        self.load_equipment()

    def delete_equipment(self):
        selected = self.equip_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите оборудование")
            return

        item = self.equip_tree.item(selected[0])
        equip_id = item['values'][0]

        if messagebox.askyesno("Подтверждение", "Удалить оборудование?"):
            self.db.delete_equipment(equip_id)
            messagebox.showinfo("Успех", "Оборудование удалено")
            self.load_equipment()