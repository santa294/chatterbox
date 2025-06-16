import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import datetime
import json
from support_platform import Platform

class SupportApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.platform = Platform()
        self.platform.generate_operators(10)
        self.platform.generate_users(20)

        # Применение современной темы
        style = ttk.Style()
        style.theme_use('clam')

        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):
        self.title("Платформа поддержки")
        self.geometry("800x600")

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=1, fill='both')

        self.users_tab = ttk.Frame(self.notebook)
        self.operators_tab = ttk.Frame(self.notebook)
        self.export_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.users_tab, text="Пользователи")
        self.notebook.add(self.operators_tab, text="Операторы")
        self.notebook.add(self.export_tab, text="Экспорт данных")

        self.setup_users_tab()
        self.setup_operators_tab()
        self.setup_export_tab()

        tk.Label(self, text="Поиск чата по ID:").pack(side='top')
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self, textvariable=self.search_var)
        search_entry.pack(side='top')
        tk.Button(self, text="Найти чат", command=self.find_chat).pack(side='top')

    def setup_users_tab(self):
        tk.Label(self.users_tab, text="Выберите пользователя:").grid(row=0, column=0, padx=5, pady=5)
        self.user_var = tk.StringVar()
        self.user_combobox = ttk.Combobox(self.users_tab, textvariable=self.user_var, width=40)
        self.user_combobox['values'] = [f"{user.full_name} (ID:{user.id})" for user in self.platform.users]
        self.user_combobox.grid(row=0, column=1, padx=5, pady=5)

        self.create_chat_button = ttk.Button(self.users_tab, text="Создать чат", command=self.create_chat)
        self.create_chat_button.grid(row=0, column=2, padx=5, pady=5)

        self.users_tree = ttk.Treeview(self.users_tab, columns=('ID', 'Status', 'Operator', 'CSAT'), show='headings')
        self.users_tree.heading('ID', text='ID чата')
        self.users_tree.heading('Status', text='Статус')
        self.users_tree.heading('Operator', text='Оператор')
        self.users_tree.heading('CSAT', text='CSAT')
        self.users_tree.column('ID', width=50)
        self.users_tree.column('Status', width=100)
        self.users_tree.column('Operator', width=200)
        self.users_tree.column('CSAT', width=50)

        vsb = ttk.Scrollbar(self.users_tab, orient="vertical", command=self.users_tree.yview)
        hsb = ttk.Scrollbar(self.users_tab, orient="horizontal", command=self.users_tree.xview)
        self.users_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.users_tree.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=5, pady=5)
        vsb.grid(row=1, column=3, sticky='ns')
        hsb.grid(row=2, column=0, columnspan=3, sticky='ew')

        self.user_details_frame = ttk.Frame(self.users_tab)
        self.user_details_frame.grid(row=3, column=0, columnspan=4, sticky='ew', padx=5, pady=5)

        self.users_tab.grid_rowconfigure(1, weight=1)
        self.users_tab.grid_columnconfigure(0, weight=1)
        self.users_tab.grid_columnconfigure(1, weight=1)
        self.users_tab.grid_columnconfigure(2, weight=1)

        self.user_combobox.bind('<<ComboboxSelected>>', lambda event: self.update_users_tree())
        self.users_tree.bind('<<TreeviewSelect>>', lambda event: self.update_user_details())

    def create_chat(self):
        selection = self.user_var.get()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите пользователя")
            return
        user_id = int(selection.split('ID:')[1].strip(')'))
        user = next(u for u in self.platform.users if u.id == user_id)

        dialog = tk.Toplevel(self)
        dialog.title("Создать чат")
        tk.Label(dialog, text="Введите начальное сообщение:").pack()
        message_entry = tk.Entry(dialog)
        message_entry.pack()

        def send():
            text = message_entry.get()
            if text:
                try:
                    chat = self.platform.create_chat(user)
                    timestamp = datetime.datetime.now()
                    chat.add_message('user', text, timestamp)
                    self.update_users_tree()
                    self.update_operators_tree()
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))

        tk.Button(dialog, text="Отправить", command=send).pack()

    def update_users_tree(self):
        selection = self.user_var.get()
        if not selection:
            return
        user_id = int(selection.split('ID:')[1].strip(')'))

        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        chats = [chat for chat in self.platform.chats if chat.user_id == user_id]
        for chat in chats:
            operator = next(op for op in self.platform.operators if op.id == chat.operator_id)
            csat = chat.csat if chat.csat is not None else "Не установлено"
            self.users_tree.insert('', 'end', values=(chat.id, chat.status, operator.full_name, csat))

    def update_user_details(self):
        selected = self.users_tree.selection()
        if not selected:
            return
        item = self.users_tree.item(selected[0])
        chat_id = int(item['values'][0])
        chat = next(c for c in self.platform.chats if c.id == chat_id)

        for widget in self.user_details_frame.winfo_children():
            widget.destroy()

        tk.Label(self.user_details_frame, text="ID чата:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        tk.Label(self.user_details_frame, text=str(chat.id)).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        tk.Label(self.user_details_frame, text="Статус:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tk.Label(self.user_details_frame, text=chat.status).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        operator = next(op for op in self.platform.operators if op.id == chat.operator_id)
        tk.Label(self.user_details_frame, text="Оператор:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        tk.Label(self.user_details_frame, text=operator.full_name).grid(row=2, column=1, sticky='w', padx=5, pady=5)

        if chat.status == 'closed' and chat.csat is None:
            tk.Label(self.user_details_frame, text="Установить CSAT:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
            csat_var = tk.StringVar()
            csat_combobox = ttk.Combobox(self.user_details_frame, textvariable=csat_var, values=[1,2,3,4,5])
            csat_combobox.grid(row=3, column=1, sticky='w', padx=5, pady=5)
            def set_csat():
                score = int(csat_var.get())
                self.platform.set_csat(chat, score)
                self.update_users_tree()
                self.update_user_details()
            tk.Button(self.user_details_frame, text="Установить CSAT", command=set_csat).grid(row=4, column=0, columnspan=2, pady=5)
        else:
            csat = chat.csat if chat.csat is not None else "Не установлено"
            tk.Label(self.user_details_frame, text="CSAT:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
            tk.Label(self.user_details_frame, text=str(csat)).grid(row=3, column=1, sticky='w', padx=5, pady=5)

        tk.Button(self.user_details_frame, text="Просмотреть сообщения", command=lambda: self.view_messages(chat)).grid(row=5, column=0, columnspan=2, pady=5)
        if chat.status == 'open' or chat.status == 'in_progress':
            tk.Button(self.user_details_frame, text="Отправить сообщение", command=lambda: self.add_user_message(chat)).grid(row=6, column=0, columnspan=2, pady=5)

    def add_user_message(self, chat):
        dialog = tk.Toplevel(self)
        dialog.title("Отправить сообщение")
        tk.Label(dialog, text="Введите сообщение:").pack()
        message_entry = tk.Entry(dialog)
        message_entry.pack()

        def send():
            text = message_entry.get()
            if text:
                timestamp = datetime.datetime.now()
                chat.add_message('user', text, timestamp)
                dialog.destroy()
                self.update_users_tree()
                self.update_operators_tree()

        tk.Button(dialog, text="Отправить", command=send).pack()

    def view_messages(self, chat):
        dialog = tk.Toplevel(self)
        dialog.title(f"Сообщения чата {chat.id}")
        text_widget = tk.Text(dialog)
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar = tk.Scrollbar(dialog, command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget.config(yscrollcommand=scrollbar.set)
        for msg in chat.messages:
            sender = 'Пользователь' if msg['sender'] == 'user' else 'Оператор'
            timestamp = datetime.datetime.fromisoformat(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            text = msg['text']
            text_widget.insert('end', f"{sender} в {timestamp}: {text}\n")
        text_widget.config(state='disabled')

    def setup_operators_tab(self):
        tk.Label(self.operators_tab, text="Выберите оператора:").grid(row=0, column=0, padx=5, pady=5)
        self.operator_var = tk.StringVar()
        self.operator_combobox = ttk.Combobox(self.operators_tab, textvariable=self.operator_var, width=40)
        self.operator_combobox['values'] = [f"{op.full_name} (ID:{op.id})" for op in self.platform.operators]
        self.operator_combobox.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.operators_tab, text="Фильтр по статусу:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_var = tk.StringVar(value="Все")
        filter_combobox = ttk.Combobox(self.operators_tab, textvariable=self.filter_var, values=["Все", "Открытые", "Закрытые", "В работе"])
        filter_combobox.grid(row=0, column=3, padx=5, pady=5)

        self.operators_tree = ttk.Treeview(self.operators_tab, columns=('ID', 'User', 'Status'), show='headings')
        self.operators_tree.heading('ID', text='ID чата')
        self.operators_tree.heading('User', text='Пользователь')
        self.operators_tree.heading('Status', text='Статус')
        self.operators_tree.column('ID', width=50)
        self.operators_tree.column('User', width=200)
        self.operators_tree.column('Status', width=100)

        vsb = ttk.Scrollbar(self.operators_tab, orient="vertical", command=self.operators_tree.yview)
        hsb = ttk.Scrollbar(self.operators_tab, orient="horizontal", command=self.operators_tree.xview)
        self.operators_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.operators_tree.grid(row=1, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)
        vsb.grid(row=1, column=4, sticky='ns')
        hsb.grid(row=2, column=0, columnspan=4, sticky='ew')

        self.operator_details_frame = ttk.Frame(self.operators_tab)
        self.operator_details_frame.grid(row=3, column=0, columnspan=5, sticky='ew', padx=5, pady=5)

        self.operators_tab.grid_rowconfigure(1, weight=1)
        self.operators_tab.grid_columnconfigure(0, weight=1)
        self.operators_tab.grid_columnconfigure(1, weight=1)

        self.operator_combobox.bind('<<ComboboxSelected>>', lambda event: self.update_operators_tree())
        self.operators_tree.bind('<<TreeviewSelect>>', lambda event: self.update_operator_details())
        filter_combobox.bind('<<ComboboxSelected>>', lambda event: self.update_operators_tree())

    def update_operators_tree(self):
        selection = self.operator_var.get()
        if not selection:
            return
        operator_id = int(selection.split('ID:')[1].strip(')'))
        filter_selection = self.filter_var.get()

        for item in self.operators_tree.get_children():
            self.operators_tree.delete(item)

        chats = [chat for chat in self.platform.chats if chat.operator_id == operator_id]
        if filter_selection == "Открытые":
            chats = [chat for chat in chats if chat.status == 'open']
        elif filter_selection == "Закрытые":
            chats = [chat for chat in chats if chat.status == 'closed']
        elif filter_selection == "В работе":
            chats = [chat for chat in chats if chat.status == 'in_progress']
        for chat in chats:
            user = next(u for u in self.platform.users if u.id == chat.user_id)
            self.operators_tree.insert('', 'end', values=(chat.id, user.full_name, chat.status))

    def update_operator_details(self):
        selected = self.operators_tree.selection()
        if not selected:
            return
        item = self.operators_tree.item(selected[0])
        chat_id = int(item['values'][0])
        chat = next(c for c in self.platform.chats if c.id == chat_id)

        for widget in self.operator_details_frame.winfo_children():
            widget.destroy()

        tk.Label(self.operator_details_frame, text="ID чата:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        tk.Label(self.operator_details_frame, text=str(chat.id)).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        user = next(u for u in self.platform.users if u.id == chat.user_id)
        tk.Label(self.operator_details_frame, text="Пользователь:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tk.Label(self.operator_details_frame, text=user.full_name).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        tk.Label(self.operator_details_frame, text="Статус:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        tk.Label(self.operator_details_frame, text=chat.status).grid(row=2, column=1, sticky='w', padx=5, pady=5)

        if chat.status == 'open':
            tk.Button(self.operator_details_frame, text="Добавить сообщение", command=lambda: self.add_message(chat)).grid(row=3, column=0, columnspan=2, pady=5)
            tk.Button(self.operator_details_frame, text="Закрыть чат", command=lambda: self.close_chat(chat)).grid(row=4, column=0, columnspan=2, pady=5)
            tk.Button(self.operator_details_frame, text="Отметить как в работе", command=lambda: self.set_chat_in_progress(chat)).grid(row=5, column=0, columnspan=2, pady=5)
        elif chat.status == 'in_progress':
            tk.Button(self.operator_details_frame, text="Добавить сообщение", command=lambda: self.add_message(chat)).grid(row=3, column=0, columnspan=2, pady=5)
            tk.Button(self.operator_details_frame, text="Закрыть чат", command=lambda: self.close_chat(chat)).grid(row=4, column=0, columnspan=2, pady=5)

        tk.Button(self.operator_details_frame, text="Просмотреть сообщения", command=lambda: self.view_messages(chat)).grid(row=6, column=0, columnspan=2, pady=5)

    def add_message(self, chat):
        dialog = tk.Toplevel(self)
        dialog.title("Добавить сообщение")
        tk.Label(dialog, text="Введите сообщение:").pack()
        message_entry = tk.Entry(dialog)
        message_entry.pack()

        def send():
            text = message_entry.get()
            if text:
                timestamp = datetime.datetime.now()
                chat.add_message('operator', text, timestamp)
                dialog.destroy()
                self.update_users_tree()
                self.update_operators_tree()

        tk.Button(dialog, text="Отправить", command=send).pack()

    def close_chat(self, chat):
        self.platform.close_chat(chat)
        self.update_users_tree()
        self.update_operators_tree()
        self.update_user_details()
        self.update_operator_details()

    def set_chat_in_progress(self, chat):
        chat.set_in_progress()
        self.update_users_tree()
        self.update_operators_tree()
        self.update_operator_details()

    def setup_export_tab(self):
        tk.Button(self.export_tab, text="Экспорт всех чатов", command=lambda: self.export_data(self.platform.export_all_chats(), "all_chats.json")).grid(row=0, column=0, pady=5)
        tk.Button(self.export_tab, text="Экспорт операторов", command=lambda: self.export_data(self.platform.export_operators(), "operators.json")).grid(row=1, column=0, pady=5)
        tk.Button(self.export_tab, text="Экспорт пользователей", command=lambda: self.export_data(self.platform.export_users(), "users.json")).grid(row=2, column=0, pady=5)

        tk.Label(self.export_tab, text="Экспорт чатов по оператору:").grid(row=3, column=0, pady=5)
        self.export_operator_var = tk.StringVar()
        export_operator_combobox = ttk.Combobox(self.export_tab, textvariable=self.export_operator_var, width=40)
        export_operator_combobox['values'] = [f"{op.full_name} (ID:{op.id})" for op in self.platform.operators]
        export_operator_combobox.grid(row=4, column=0, pady=5)
        tk.Button(self.export_tab, text="Экспорт", command=lambda: self.export_chats_by_operator()).grid(row=5, column=0, pady=5)

        tk.Label(self.export_tab, text="Экспорт чатов по пользователю:").grid(row=6, column=0, pady=5)
        self.export_user_var = tk.StringVar()
        export_user_combobox = ttk.Combobox(self.export_tab, textvariable=self.export_user_var, width=40)
        export_user_combobox['values'] = [f"{u.full_name} (ID:{u.id})" for u in self.platform.users]
        export_user_combobox.grid(row=7, column=0, pady=5)
        tk.Button(self.export_tab, text="Экспорт", command=lambda: self.export_chats_by_user()).grid(row=8, column=0, pady=5)

        tk.Button(self.export_tab, text="Экспорт чатов по статусу", command=self.export_chats_by_status).grid(row=9, column=0, pady=5)

    def export_data(self, data, default_filename):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", initialfile=default_filename)
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data)
            messagebox.showinfo("Успех", "Данные успешно экспортированы")

    def export_chats_by_operator(self):
        selection = self.export_operator_var.get()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите оператора")
            return
        operator_id = int(selection.split('ID:')[1].strip(')'))
        data = self.platform.export_chats_by_operator(operator_id)
        self.export_data(data, f"operator_{operator_id}_chats.json")

    def export_chats_by_user(self):
        selection = self.export_user_var.get()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите пользователя")
            return
        user_id = int(selection.split('ID:')[1].strip(')'))
        data = self.platform.export_chats_by_user(user_id)
        self.export_data(data, f"user_{user_id}_chats.json")

    def export_chats_by_status(self):
        dialog = tk.Toplevel(self)
        dialog.title("Экспорт чатов по статусу")
        tk.Label(dialog, text="Выберите статус:").pack()
        status_var = tk.StringVar()
        status_combobox = ttk.Combobox(dialog, textvariable=status_var, values=["open", "closed", "in_progress"])
        status_combobox.pack()

        def export():
            status = status_var.get()
            if status:
                chats = [chat for chat in self.platform.chats if chat.status == status]
                data = json.dumps([chat.to_dict() for chat in chats], indent=4, ensure_ascii=False)
                self.export_data(data, f"{status}_chats.json")
                dialog.destroy()

        tk.Button(dialog, text="Экспорт", command=export).pack()

    def find_chat(self):
        chat_id = self.search_var.get()
        if not chat_id:
            messagebox.showerror("Ошибка", "Введите ID чата")
            return
        try:
            chat_id = int(chat_id)
            chat = next(c for c in self.platform.chats if c.id == chat_id)
            self.show_chat_details(chat)
        except StopIteration:
            messagebox.showerror("Ошибка", "Чат не найден")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный ID чата")

    def show_chat_details(self, chat):
        dialog = tk.Toplevel(self)
        dialog.title(f"Детали чата {chat.id}")
        tk.Label(dialog, text=f"ID чата: {chat.id}").pack()
        tk.Label(dialog, text=f"Статус: {chat.status}").pack()
        user = next(u for u in self.platform.users if u.id == chat.user_id)
        tk.Label(dialog, text=f"Пользователь: {user.full_name}").pack()
        operator = next(op for op in self.platform.operators if op.id == chat.operator_id)
        tk.Label(dialog, text=f"Оператор: {operator.full_name}").pack()
        tk.Label(dialog, text=f"CSAT: {chat.csat if chat.csat is not None else 'Не установлено'}").pack()
        tk.Button(dialog, text="Просмотреть сообщения", command=lambda: self.view_messages(chat)).pack()

if __name__ == "__main__":
    app = SupportApp()
    app.mainloop()
