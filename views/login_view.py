import tkinter as tk
from tkinter import messagebox, simpledialog
from controllers import auth_controller
import theme_fisio

class LoginWindow:
    def __init__(self, master):
        self.root = master

        theme_fisio.apply_theme(self.root)
        theme_fisio.paint(self.root)

        self.root.title("FisioManager - Accesso")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.logged_in_user = None

        tk.Label(self.root, text="Email:").pack(fill='x', padx=20, pady=(30, 5))
        self.email_entry = tk.Entry(self.root, width=40)
        self.email_entry.pack(fill='x', padx=20, pady=5)

        tk.Label(self.root, text="Password:").pack(fill='x', padx=20, pady=(10, 5))
        self.pwd_entry = tk.Entry(self.root, show="*", width=40)
        self.pwd_entry.pack(fill='x', padx=20, pady=5)

        tk.Button(self.root, text="Accedi", width=20, command=self.login).pack(pady=(20, 5))
        tk.Button(self.root, text="Recupera Password", width=20, command=self.forgot_password).pack()

    def login(self):
        email = self.email_entry.get().strip()
        pwd = self.pwd_entry.get().strip()
        if not email or not pwd:
            messagebox.showwarning('Campi mancanti', 'Inserisci email e password')
            return
        user = auth_controller.attempt_login(email, pwd)
        if user:
            self.logged_in_user = user
            messagebox.showinfo('Successo', f'Benvenuto {user.nome}')
            self.root.destroy()
        else:
            messagebox.showerror('Errore', 'Credenziali non valide')

    def forgot_password(self):
        email = simpledialog.askstring('Recupero', 'Inserisci email:', parent=self.root)
        if email:
            if auth_controller.recover_password(email.strip()):
                messagebox.showinfo('Recupero', 'Email di reset inviata (simulazione).')
            else:
                messagebox.showinfo('Recupero', 'Email non trovata.')
