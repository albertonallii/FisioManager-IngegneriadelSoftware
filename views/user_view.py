import tkinter as tk
from tkinter import messagebox
from controllers import user_controller
import theme_fisio

class UserWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        theme_fisio.paint(self)
        self.title("Gestione Utenti")
        self.geometry("520x440")

        self.selected_user_id = None
        self._listbox_user_ids = []

        list_frame = tk.Frame(self)
        list_frame.pack(side="top", fill="both", expand=True, padx=6, pady=6)

        tk.Label(list_frame, text="Utenti registrati:").pack(anchor="w")

        self.user_listbox = tk.Listbox(list_frame)
        self.user_listbox.config(bg="white", fg="black")
        self.user_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.user_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.user_listbox.config(yscrollcommand=scrollbar.set)

        self.user_listbox.bind("<<ListboxSelect>>", self.on_select)

        form_frame = tk.Frame(self)
        form_frame.pack(side="bottom", fill="x", padx=6, pady=6)

        tk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky="e", pady=2)
        self.nome_entry = tk.Entry(form_frame, bg="white", fg="black", width=28)
        self.nome_entry.grid(row=0, column=1, pady=2, sticky="w")

        tk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky="e", pady=2)
        self.email_entry = tk.Entry(form_frame, bg="white", fg="black", width=28)
        self.email_entry.grid(row=1, column=1, pady=2, sticky="w")

        tk.Label(form_frame, text="Password:").grid(row=2, column=0, sticky="e", pady=2)
        self.pwd_entry = tk.Entry(form_frame, show="*", bg="white", fg="black", width=28)
        self.pwd_entry.grid(row=2, column=1, pady=2, sticky="w")

        tk.Label(form_frame, text="Ruolo:").grid(row=3, column=0, sticky="e", pady=2)
        self.ruolo_var = tk.StringVar(value="Fisioterapista")
        ruolo_options = ("Fisioterapista", "Admin")
        self.ruolo_menu = tk.OptionMenu(form_frame, self.ruolo_var, *ruolo_options)
        self.ruolo_menu.grid(row=3, column=1, pady=2, sticky="w")

        for entry in (self.nome_entry, self.email_entry, self.pwd_entry):
            entry.configure(borderwidth=1, relief="solid")

        btns = tk.Frame(form_frame)
        btns.grid(row=4, column=0, columnspan=2, pady=8)

        self.add_btn = tk.Button(btns, text="Aggiungi Utente", command=self.add_user)
        self.add_btn.pack(side="left", padx=5)

        self.update_btn = tk.Button(btns, text="Aggiorna Utente", command=self.update_user, state="disabled")
        self.update_btn.pack(side="left", padx=5)
        self.update_btn.configure(disabledforeground="#000000")

        self.delete_btn = tk.Button(btns, text="Elimina Utente", command=self.delete_user, state="disabled")
        self.delete_btn.pack(side="left", padx=5)
        self.delete_btn.configure(disabledforeground="#000000")

        self.refresh_list()

    def on_select(self, _event=None):
        sel = self.user_listbox.curselection()
        if not sel:
            self.selected_user_id = None
            self.update_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            return

        idx = sel[0]
        if not (0 <= idx < len(self._listbox_user_ids)):
            self.selected_user_id = None
            self.update_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            return

        uid = self._listbox_user_ids[idx]
        self.selected_user_id = uid

        users = user_controller.get_all_users()
        u = next((x for x in users if x.id == uid), None)
        if not u:
            self.update_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            return

        self.nome_entry.delete(0, tk.END)
        self.nome_entry.insert(0, u.nome or "")

        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, u.email or "")

        self.pwd_entry.delete(0, tk.END)

        role_label = "Fisioterapista" if str(u.ruolo).lower() in ("fisioterapista", "physio") else "Admin"
        self.ruolo_var.set(role_label)

        # abilitati -> testo bianco
        self.update_btn.config(state="normal", fg="white")
        self.delete_btn.config(state="normal", fg="white")

    def refresh_list(self):
        users = user_controller.get_all_users()
        users.sort(key=lambda u: u.id)

        self.user_listbox.delete(0, tk.END)
        self._listbox_user_ids.clear()

        for i, u in enumerate(users, start=1):
            role_name = "Fisioterapista" if str(u.ruolo).lower() in ("fisioterapista", "physio") else "Admin"
            self.user_listbox.insert(
                tk.END,
                f"{i}. {u.nome} ({u.email}) - {role_name}"
            )
            self._listbox_user_ids.append(u.id)

        self.selected_user_id = None
        # tornano disabilitati (testo nero)
        self.update_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
        self.nome_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.pwd_entry.delete(0, tk.END)
        self.ruolo_var.set("Fisioterapista")

    def add_user(self):
        nome = self.nome_entry.get().strip()
        email = self.email_entry.get().strip()
        pwd = self.pwd_entry.get().strip()
        ruolo = self.ruolo_var.get().strip()

        if not nome or not email or not pwd:
            messagebox.showwarning("Campi obbligatori", "Inserisci nome, email e password.")
            return

        user = user_controller.create_new_user(nome, email, pwd, ruolo)
        if not user:
            messagebox.showerror("Errore", "Impossibile creare utente. Email forse già utilizzata.")
        else:
            messagebox.showinfo("Successo", "Utente creato correttamente.")
            self.nome_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.pwd_entry.delete(0, tk.END)
            self.ruolo_var.set("Fisioterapista")
        self.refresh_list()

    def update_user(self):
        "Aggiorna i dati dell'utente selezionato. La password viene aggiornata solo se non vuota."
        if self.selected_user_id is None:
            messagebox.showwarning("Selezione mancante", "Seleziona un utente dall'elenco.")
            return

        nome = self.nome_entry.get().strip()
        email = self.email_entry.get().strip()
        pwd = self.pwd_entry.get().strip()  # se vuoto, non aggiornare la password
        ruolo = self.ruolo_var.get().strip()

        if not nome or not email:
            messagebox.showwarning("Campi obbligatori", "Nome ed email sono obbligatori.")
            return

        new_pwd = pwd if pwd else None

        ok = user_controller.update_user(
            self.selected_user_id,
            nome=nome,
            email=email,
            password=new_pwd,
            ruolo=ruolo
        )
        if not ok:
            messagebox.showerror("Errore", "Impossibile aggiornare l'utente (email già in uso o utente non trovato).")
            return

        messagebox.showinfo("Aggiornato", "Utente aggiornato correttamente.")
        self.pwd_entry.delete(0, tk.END)
        self.refresh_list()

    def delete_user(self):
        "Elimina definitivamente l'utente selezionato."
        if self.selected_user_id is None:
            messagebox.showwarning("Selezione mancante", "Seleziona un utente dall'elenco.")
            return

        if not messagebox.askyesno("Conferma eliminazione", "Eliminare definitivamente questo utente?"):
            return

        ok = user_controller.delete_user(self.selected_user_id)
        if not ok:
            messagebox.showerror("Errore", "Impossibile eliminare l'utente.")
            return

        messagebox.showinfo("Eliminato", "Utente eliminato correttamente.")
        self.refresh_list()
