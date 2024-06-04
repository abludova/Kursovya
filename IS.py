import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import bcrypt
import ttkbootstrap as ttkb

def get_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=LAPTOP-1EP0LPKF\\SQLEXPRESS;"  # Имя сервера и экземпляра
        "DATABASE=Ariana_database;"  # Имя базы данных
        "UID=test_user;"  # Имя нового пользователя
        "PWD=StrongPassword123"  # Пароль нового пользователя
    )
    return pyodbc.connect(conn_str)
def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 11

def is_valid_email(email):
    return "@" in email and "." in email
def login():
    username = entry_username.get()
    password = entry_password.get().encode('utf-8')

    # Проверка логина и пароля
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Password, Role FROM Users WHERE Username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password, row[0].encode('utf-8')):
        role = row[1]
        if role == "client":
            open_client_window()
        elif role == "admin":
            open_admin_window()
    else:
        messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")

def register():
    username = entry_username.get()
    password = entry_password.get().encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (Username, Password, Role) VALUES (?, ?, ?)", (username, hashed, "client"))
    conn.commit()
    conn.close()
    messagebox.showinfo("Успех", "Пользователь зарегистрирован")
def open_client_window():
    client_window = tk.Toplevel(root)
    client_window.title("Клиент")

    frame_form = ttk.Frame(client_window, padding="10")
    frame_form.grid(row=0, column=0, sticky=tk.W)

    # Поля ввода
    ttk.Label(frame_form, text="Имя клиента").grid(row=0, column=0, padx=5, pady=5)
    entry_name = ttk.Entry(frame_form)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame_form, text="Телефон").grid(row=1, column=0, padx=5, pady=5)
    entry_phone = ttk.Entry(frame_form)
    entry_phone.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(frame_form, text="Адрес").grid(row=2, column=0, padx=5, pady=5)
    entry_address = ttk.Entry(frame_form)
    entry_address.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(frame_form, text="Электронная почта").grid(row=3, column=0, padx=5, pady=5)
    entry_email = ttk.Entry(frame_form)
    entry_email.grid(row=3, column=1, padx=5, pady=5)

    # Выпадающий список для типов объектов
    ttk.Label(frame_form, text="Тип объекта").grid(row=4, column=0, padx=5, pady=5)
    object_types = ["Квартира", "Дом", "Офис", "Склад"]
    combo_object_type = ttk.Combobox(frame_form, values=object_types, state="readonly")
    combo_object_type.grid(row=4, column=1, padx=5, pady=5)

    # Выпадающий список для видов уборки
    ttk.Label(frame_form, text="Вид уборки").grid(row=5, column=0, padx=5, pady=5)
    cleaning_types = ["Общая", "Генеральная", "Послеремонтная", "Ежедневная"]
    combo_cleaning_type = ttk.Combobox(frame_form, values=cleaning_types, state="readonly")
    combo_cleaning_type.grid(row=5, column=1, padx=5, pady=5)

    # Поле для отображения стоимости
    ttk.Label(frame_form, text="Стоимость").grid(row=6, column=0, padx=5, pady=5)
    label_cost = ttk.Label(frame_form, text="")
    label_cost.grid(row=6, column=1, padx=5, pady=5)

    # Функция для расчета стоимости
    def calculate_cost():
        cleaning_type = combo_cleaning_type.get()
        if cleaning_type:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT СтоимостьУслуги FROM Услуги WHERE НазваниеУслуги=?", (cleaning_type,))
                row = cursor.fetchone()
                if row:
                    cost = row[0]
                    label_cost.config(text=str(cost))
                else:
                    label_cost.config(text="Не найдено")
                conn.close()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    combo_cleaning_type.bind("<<ComboboxSelected>>", lambda _: calculate_cost())


    # Кнопка для отправки данных
    ttk.Button(frame_form, text="Отправить", command=lambda: submit_client_form(entry_name, entry_phone, entry_address, entry_email, combo_object_type, combo_cleaning_type, label_cost)).grid(row=7, columnspan=2, padx=5, pady=5)

    # Кнопка для открытия окна отзыва
    ttk.Button(frame_form, text="Оставить отзыв", command=open_feedback_window).grid(row=8, columnspan=2, padx=5, pady=5)
def submit_client_form(entry_name, entry_phone, entry_address, entry_email, combo_object_type, combo_cleaning_type, label_cost):
    name = entry_name.get()
    phone = entry_phone.get()
    address = entry_address.get()
    email = entry_email.get()
    object_type = combo_object_type.get()
    cleaning_type = combo_cleaning_type.get()
    cost = label_cost.cget("text")

    if not name or not phone or not address or not email or not object_type or not cleaning_type or not cost:
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
        return

    if not is_valid_phone(phone):
        messagebox.showerror("Ошибка", "Введите корректный номер телефона (11 цифр)")
        return

    if not is_valid_email(email):
        messagebox.showerror("Ошибка", "Введите корректный адрес электронной почты")
        return

    service_name = f"{object_type} - {cleaning_type}"

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Клиенты (ИмяКлиента, Телефон, Адрес, ЭлектроннаяПочта) VALUES (?, ?, ?, ?)",
                       (name, phone, address, email))
        cursor.execute("INSERT INTO ОбъектыУборки (КлиентID, ТипОбъекта, МестоПроведенияУборки) VALUES ((SELECT MAX(КлиентID) FROM Клиенты), ?, ?)",
                       (object_type, address))
        cursor.execute("INSERT INTO Уборки (ОбъектУборкиID, ВидУборки, ДатаУборки) VALUES ((SELECT MAX(ОбъектУборкиID) FROM ОбъектыУборки), ?, GETDATE())",
                       (cleaning_type,))
        cursor.execute("INSERT INTO УборкиУслуги (УборкаID, УслугаID, Количество) VALUES ((SELECT MAX(УборкаID) FROM Уборки), (SELECT УслугаID FROM Услуги WHERE НазваниеУслуги=?), 1)",
                       (service_name,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Данные успешно отправлены")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
def open_feedback_window():
    feedback_window = tk.Toplevel(root)
    feedback_window.title("Оставить отзыв")

    frame_feedback = ttk.Frame(feedback_window, padding="10")
    frame_feedback.grid(row=0, column=0, sticky=tk.W)

    ttk.Label(frame_feedback, text="Отзыв").grid(row=0, column=0, padx=5, pady=5)
    entry_feedback = ttk.Entry(frame_feedback)
    entry_feedback.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame_feedback, text="Оценка").grid(row=1, column=0, padx=5, pady=5)
    rating_values = [1, 2, 3, 4, 5]
    combo_rating = ttk.Combobox(frame_feedback, values=rating_values, state="readonly")
    combo_rating.grid(row=1, column=1, padx=5, pady=5)

    # Кнопка для отправки отзыва
    ttk.Button(frame_feedback, text="Оставить отзыв", command=lambda: submit_feedback(entry_feedback, combo_rating)).grid(row=2, columnspan=2, padx=5, pady=5)
def submit_feedback(entry_feedback, combo_rating):
    feedback = entry_feedback.get()
    rating = combo_rating.get()

    if not feedback or not rating:
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
        return

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Оценка должна быть числом от 1 до 5")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Отзывы (УборкаID, ТекстОтзыва, Оценка, ДатаОтзыва) VALUES ((SELECT MAX(УборкаID) FROM Уборки), ?, ?, GETDATE())",
                       (feedback, rating))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Отзыв успешно отправлен")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

#Функция для получения списка сотрудников
def get_employees():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ИмяСотрудника FROM Сотрудники")
        rows = cursor.fetchall()
        employee_list = [row[0] for row in rows]
        conn.close()
        return employee_list
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
        return []

# Дополнение к предыдущему коду для формы администратора
def open_admin_window():
    admin_window = tk.Toplevel(root)
    admin_window.title("Администратор")

    frame_admin = ttk.Frame(admin_window, padding="10")
    frame_admin.grid(row=0, column=0, sticky=tk.W)

    ttk.Label(frame_admin, text="Административная панель").grid(row=0, column=0, columnspan=4, padx=5, pady=5)

    # Создание фрейма для дерева и полос прокрутки
    frame_tree = ttk.Frame(admin_window)
    frame_tree.grid(row=1, column=0, padx=5, pady=5, columnspan=4, sticky=tk.EW)

    # Вертикальная полоса прокрутки
    tree_scroll_y = ttk.Scrollbar(frame_tree, orient="vertical")
    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    # Горизонтальная полоса прокрутки
    tree_scroll_x = ttk.Scrollbar(frame_tree, orient="horizontal")
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    # Таблица для просмотра заказов
    tree_orders = ttk.Treeview(frame_tree, columns=("УборкаID", "ПолноеИмя", "Адрес", "Телефон", "ЭлектроннаяПочта", "ВидУборки", "ДатаУборки"), show="headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
    tree_orders.heading("УборкаID", text="ID уборки")
    tree_orders.heading("ПолноеИмя", text="Имя клиента")
    tree_orders.heading("Адрес", text="Адрес")
    tree_orders.heading("Телефон", text="Телефон")
    tree_orders.heading("ЭлектроннаяПочта", text="Электронная почта")
    tree_orders.heading("ВидУборки", text="Вид уборки")
    tree_orders.heading("ДатаУборки", text="Дата уборки")
    tree_orders.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Привязка полос прокрутки к дереву
    tree_scroll_y.config(command=tree_orders.yview)
    tree_scroll_x.config(command=tree_orders.xview)

    # Кнопка для загрузки данных
    ttk.Button(admin_window, text="Загрузить данные", command=lambda: load_orders(tree_orders)).grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky=tk.EW)

    # Поле для выбора сотрудника
    ttk.Label(admin_window, text="Сотрудник").grid(row=3, column=1, padx=(5, 0), pady=5, sticky=tk.W)
    combo_employee = ttk.Combobox(admin_window, values=get_employees(), state="readonly")
    combo_employee.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)

    # Поле для ввода количества часов
    ttk.Label(admin_window, text="Отработанные часы").grid(row=4, column=1, padx=(5, 0), pady=5, sticky=tk.W)
    entry_hours_worked = ttk.Entry(admin_window)
    entry_hours_worked.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)

    # Кнопка для назначения сотрудника
    ttk.Button(admin_window, text="Назначить сотрудника", command=lambda: assign_employee(tree_orders, combo_employee, entry_hours_worked)).grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky=tk.EW)

# Функция для загрузки заказов
def load_orders(tree):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                Уборки.УборкаID, 
                Клиенты.ИмяКлиента,
                Клиенты.Адрес,
                Клиенты.Телефон,
                Клиенты.ЭлектроннаяПочта,
                Уборки.ВидУборки, 
                Уборки.ДатаУборки 
            FROM Уборки 
            JOIN ОбъектыУборки ON Уборки.ОбъектУборкиID = ОбъектыУборки.ОбъектУборкиID 
            JOIN Клиенты ON ОбъектыУборки.КлиентID = Клиенты.КлиентID
        """)
        rows = cursor.fetchall()
        for row in tree.get_children():
            tree.delete(row)
        for row in rows:
            full_name = row[1]
            tree.insert("", tk.END, values=(row[0], full_name, row[2], row[3], row[4], row[5], row[6]))
        conn.close()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))



# Функция для назначения сотрудника
def assign_employee(tree, combo_employee, entry_hours_worked):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите заказ")
        return

    employee_name = combo_employee.get()
    hours_worked = entry_hours_worked.get()
    if not employee_name:
        messagebox.showerror("Ошибка", "Выберите сотрудника")
        return
    if not hours_worked.isdigit():
        messagebox.showerror("Ошибка", "Введите корректное количество часов")
        return

    order_id = tree.item(selected_item[0], "values")[0]

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT СотрудникID FROM Сотрудники WHERE ИмяСотрудника = ?", (employee_name,))
        employee_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO РаботаСотрудников (СотрудникID, УборкаID, ОтработанныеЧасы) VALUES (?, ?, ?)", (employee_id, order_id, hours_worked))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Сотрудник успешно назначен")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))



# Создание главного окна
root = tk.Tk()
root.title("Вход")

# Фрейм для формы входа
frame_login = ttk.Frame(root, padding="10")
frame_login.grid(row=0, column=0, sticky=tk.W)

# Поля ввода логина и пароля
ttk.Label(frame_login, text="Имя пользователя").grid(row=0, column=0, padx=5, pady=5)
entry_username = ttk.Entry(frame_login)
entry_username.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_login, text="Пароль").grid(row=1, column=0, padx=5, pady=5)
entry_password = ttk.Entry(frame_login, show="*")
entry_password.grid(row=1, column=1, padx=5, pady=5)

# Кнопки для входа и регистрации
ttk.Button(frame_login, text="Войти", command=login).grid(row=2, columnspan=2, padx=5, pady=5)
ttk.Button(frame_login, text="Регистрация", command=register).grid(row=3, columnspan=2, padx=5, pady=5)


root.mainloop()

