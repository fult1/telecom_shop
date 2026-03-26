import tkinter as tk
from tkinter import messagebox, ttk
from database import Database
from user_panel import UserPanel
from admin_panel import AdminPanel


class TelecomShopApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Telecom Shop - Система заказа оборудования")
        self.root.geometry("400x500")

        self.db = Database()

        self.create_widgets()

    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Telecom Shop",
                               font=("Arial", 24, "bold"))
        title_label.pack(pady=20)

        subtitle_label = tk.Label(self.root, text="Система заказа телекоммуникационного оборудования",
                                  font=("Arial", 10))
        subtitle_label.pack(pady=5)

        # Фрейм для входа
        login_frame = tk.LabelFrame(self.root, text="Вход в систему", padx=20, pady=20)
        login_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        tk.Label(login_frame, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = tk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)

        tk.Label(login_frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = tk.Entry(login_frame, show="*", width=30)
        self.password_entry.grid(row=1, column=1, pady=5)

        # Кнопки
        button_frame = tk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="Войти", command=self.login,
                  bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Регистрация", command=self.register,
                  bg="#2196F3", fg="white", width=10).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Выход", command=self.root.quit,
                  bg="#f44336", fg="white", width=10).pack(side=tk.LEFT, padx=5)

        # Информация
        info_text = """
        Тестовые данные:
        Администратор: admin / admin123
        Пользователь: зарегистрируйтесь самостоятельно
        """

        info_label = tk.Label(self.root, text=info_text, font=("Arial", 8),
                              fg="gray", justify=tk.LEFT)
        info_label.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        user = self.db.authenticate(username, password)

        if user:
            if user[2] == 1:  # Администратор
                AdminPanel(self.root, self.db)
            else:  # Пользователь
                UserPanel(self.root, self.db, user[0], user[1])
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def register(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Регистрация")
        register_window.geometry("300x250")

        tk.Label(register_window, text="Регистрация нового пользователя",
                 font=("Arial", 12, "bold")).pack(pady=10)

        frame = tk.Frame(register_window)
        frame.pack(pady=20)

        tk.Label(frame, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        reg_username = tk.Entry(frame, width=20)
        reg_username.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        reg_password = tk.Entry(frame, show="*", width=20)
        reg_password.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Подтвердите:").grid(row=2, column=0, sticky=tk.W, pady=5)
        reg_confirm = tk.Entry(frame, show="*", width=20)
        reg_confirm.grid(row=2, column=1, pady=5)

        def do_register():
            username = reg_username.get()
            password = reg_password.get()
            confirm = reg_confirm.get()

            if not username or not password:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            if password != confirm:
                messagebox.showerror("Ошибка", "Пароли не совпадают")
                return

            if self.db.register_user(username, password):
                messagebox.showinfo("Успех", "Регистрация успешна! Теперь вы можете войти.")
                register_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")

        tk.Button(register_window, text="Зарегистрироваться", command=do_register,
                  bg="#4CAF50", fg="white").pack(pady=20)

    def run(self):
        self.root.mainloop()
        self.db.close()


if __name__ == "__main__":
    app = TelecomShopApp()
    app.run()