import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import theme_fisio
from controllers import patient_controller
from models.appointment import Appointment
from models.user import User


class AppointmentWindow(tk.Toplevel):
    def __init__(self, master=None, user=None):
        super().__init__(master)
        theme_fisio.paint(self)
        self.title("Gestione Agenda")
        self.geometry("900x520")

        self._pat_label_to_id = {}
        self._phys_label_to_id = {}
        self._selected_app_id = None

        left = tk.Frame(self)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(left, text="Appuntamenti").pack(anchor="w")
        self.listbox = tk.Listbox(left, exportselection=False)
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_select_fill_form)

        right = tk.LabelFrame(self, text="Nuovo/Appuntamento")
        right.pack(side="right", fill="y", padx=10, pady=10)
        right.pack_propagate(False)
        right.configure(width=360)

        r = 0
        tk.Label(right, text="Paziente").grid(row=r, column=0, sticky="e")
        self.pat_var = tk.StringVar()
        self.pat_cb = ttk.Combobox(right, textvariable=self.pat_var, state="readonly", width=28)
        self.pat_cb.grid(row=r, column=1, sticky="w")

        r += 1
        tk.Label(right, text="Fisioterapista").grid(row=r, column=0, sticky="e")
        self.phys_var = tk.StringVar()
        self.phys_cb = ttk.Combobox(right, textvariable=self.phys_var, state="readonly", width=28)
        self.phys_cb.grid(row=r, column=1, sticky="w")

        r += 1
        tk.Label(right, text="Data (YYYY-MM-DD)").grid(row=r, column=0, sticky="e")
        self.data_e = tk.Entry(right, width=16)
        self.data_e.grid(row=r, column=1, sticky="w")

        r += 1
        tk.Label(right, text="Ora (HH:MM)").grid(row=r, column=0, sticky="e")
        self.ora_e = tk.Entry(right, width=10)
        self.ora_e.grid(row=r, column=1, sticky="w")

        r += 1
        tk.Label(right, text="Trattamento").grid(row=r, column=0, sticky="e")
        self.tratt_e = tk.Entry(right, width=28)
        self.tratt_e.grid(row=r, column=1, sticky="w")

        r += 1
        btns = tk.Frame(right)
        btns.grid(row=r, column=0, columnspan=2, pady=(8, 0), sticky="w")
        tk.Button(btns, text="Crea", command=self.add_appointment).pack(side="left", padx=(0, 6))
        tk.Button(btns, text="Aggiorna", command=self.update_appointment).pack(side="left", padx=(0, 6))
        tk.Button(btns, text="Segna completato", command=self.mark_completed).pack(side="left", padx=(0, 6))
        tk.Button(btns, text="Annulla", command=self.cancel).pack(side="left", padx=(0, 6))
        tk.Button(btns, text="Elimina", command=self.delete_appointment).pack(side="left")

        self.refresh_combo_data()
        self.refresh_list()

    def refresh_combo_data(self):
        pats = patient_controller.get_all_patients()
        pats.sort(key=lambda p: (p.cognome.lower(), p.nome.lower()))
        self._pat_label_to_id = {f"{p.cognome} {p.nome} (ID {p.id})": p.id for p in pats}
        self.pat_cb["values"] = list(self._pat_label_to_id.keys())

        users = User.load_all()
        users.sort(key=lambda u: u.nome.lower())
        self._phys_label_to_id = {f"{u.nome} (ID {u.id})": u.id for u in users}
        self.phys_cb["values"] = list(self._phys_label_to_id.keys())

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        pats = {p.id: f"{p.cognome} {p.nome}" for p in patient_controller.get_all_patients()}
        users = {u.id: u.nome for u in User.load_all()}
        apps = Appointment.get_appointments()
        apps.sort(key=lambda a: (a.data, a.ora))
        for a in apps:
            p = pats.get(a.patient_id, f"ID {a.patient_id}")
            u = users.get(a.physio_id, f"ID {a.physio_id}")
            self.listbox.insert(tk.END, f"{a.data} {a.ora} — {p} — {u} — {a.stato}")

    def _get_selected_appointment(self):
        if self._selected_app_id is not None:
            apps = Appointment.get_appointments(id=self._selected_app_id)
            return apps[0] if apps else None

        sel = self.listbox.curselection()
        if not sel:
            return None
        row = self.listbox.get(sel[0])
        try:
            left = row.split(" — ", 1)[0]
            data, ora = left.split(" ")
        except Exception:
            return None
        apps = Appointment.get_appointments(data=data)
        return next((a for a in apps if a.ora == ora), None)

    def _label_for_patient(self, patient_id):
        for label, pid in self._pat_label_to_id.items():
            if pid == patient_id:
                return label
        return ""

    def _label_for_physio(self, physio_id):
        for label, uid in self._phys_label_to_id.items():
            if uid == physio_id:
                return label
        return ""

    def _on_select_fill_form(self, _event=None):
        app = self._get_selected_appointment()
        if not app:
            self._selected_app_id = None
            return
        self._selected_app_id = app.id
        self.pat_cb.set(self._label_for_patient(app.patient_id))
        self.phys_cb.set(self._label_for_physio(app.physio_id))
        self.data_e.delete(0, tk.END); self.data_e.insert(0, app.data)
        self.ora_e.delete(0, tk.END); self.ora_e.insert(0, app.ora)
        self.tratt_e.delete(0, tk.END); self.tratt_e.insert(0, app.trattamento or "")

    def add_appointment(self):
        if not self.pat_var.get() or not self.phys_var.get():
            messagebox.showwarning("Campi mancanti", "Seleziona paziente e fisioterapista.")
            return
        try:
            pid = self._pat_label_to_id[self.pat_var.get()]
            phys_id = self._phys_label_to_id[self.phys_var.get()]
        except KeyError:
            messagebox.showerror("Errore", "Selezioni non valide.")
            return

        data = self.data_e.get().strip()
        ora = self.ora_e.get().strip()
        tratt = self.tratt_e.get().strip()

        try:
            Appointment.create_appointment(pid, phys_id, data, ora, trattamento=tratt)
        except ValueError as e:
            messagebox.showerror("Conflitto", str(e))
            return

        messagebox.showinfo("OK", "Appuntamento creato.")
        self.refresh_list()

    def update_appointment(self):
        app = self._get_selected_appointment()
        if not app:
            messagebox.showwarning("Selezione mancante", "Seleziona un appuntamento da modificare.")
            return

        if not self.pat_var.get() or not self.phys_var.get():
            messagebox.showwarning("Campi mancanti", "Seleziona paziente e fisioterapista.")
            return
        try:
            new_pid = self._pat_label_to_id[self.pat_var.get()]
            new_phys = self._phys_label_to_id[self.phys_var.get()]
        except KeyError:
            messagebox.showerror("Errore", "Selezioni non valide.")
            return

        new_data = self.data_e.get().strip()
        new_ora  = self.ora_e.get().strip()
        new_tratt = self.tratt_e.get().strip()

        try:
            new_dt = datetime.strptime(f"{new_data} {new_ora}", "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Formato non valido", "Data/Ora non valide. Usa YYYY-MM-DD e HH:MM.")
            return

        durata = timedelta(hours=1)
        apps = Appointment.load_all()
        for a in apps:
            if a.id == app.id:
                continue
            if a.physio_id == new_phys and a.data == new_data and a.stato == 'programmato':
                existing_dt = datetime.strptime(f"{a.data} {a.ora}", "%Y-%m-%d %H:%M")
                if new_dt < existing_dt + durata and existing_dt < new_dt + durata:
                    messagebox.showerror(
                        "Conflitto",
                        f"L'orario {new_ora} del {new_data} si sovrappone ad un appuntamento esistente."
                    )
                    return

        for i, a in enumerate(apps):
            if a.id == app.id:
                a.patient_id = new_pid
                a.physio_id = new_phys
                a.data = new_data
                a.ora = new_ora
                a.trattamento = new_tratt
                apps[i] = a
                break

        Appointment.save_all(apps)
        messagebox.showinfo("Aggiornato", "Appuntamento aggiornato.")
        self.refresh_list()

    def mark_completed(self):
        app = self._get_selected_appointment()
        if not app:
            messagebox.showwarning("Selezione mancante", "Seleziona un appuntamento.")
            return
        Appointment.record_session(app.id)
        self.refresh_list()

    def cancel(self):
        app = self._get_selected_appointment()
        if not app:
            messagebox.showwarning("Selezione mancante", "Seleziona un appuntamento.")
            return
        Appointment.cancel_appointment(app.id)
        self.refresh_list()

    def delete_appointment(self):
        app = self._get_selected_appointment()
        if not app:
            messagebox.showwarning("Selezione mancante", "Seleziona un appuntamento da eliminare.")
            return
        if not messagebox.askyesno(
            "Conferma eliminazione",
            f"Eliminare definitivamente l'appuntamento del {app.data} alle {app.ora}?"
        ):
            return

        apps = Appointment.load_all()
        remaining = [a for a in apps if a.id != app.id]
        Appointment.save_all(remaining)

        messagebox.showinfo("Eliminato", "Appuntamento eliminato.")
        self.refresh_list()
