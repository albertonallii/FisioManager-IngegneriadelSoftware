import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import theme_fisio
from controllers import invoice_controller
from models.appointment import Appointment
from models.patient import Patient
from models.user import User
from models.invoice import Invoice


class InvoiceWindow(tk.Toplevel):
    def __init__(self, master=None, current_user=None):
        super().__init__(master)
        theme_fisio.paint(self)
        self.current_user = current_user
        self.title("Fatturazione")
        self.geometry("1100x550")

        self._app_display_to_id = {}
        self._listbox_invoice_ids = []
        self.selected_inv_id = None
        self.show_paid_mode = False

        list_frame = tk.Frame(self)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.toggle_btn = tk.Button(list_frame, text="Fatture Pagate", command=self.toggle_paid_view)
        self.toggle_btn.pack(anchor="w", pady=(0, 5))

        self.inv_listbox = tk.Listbox(list_frame)
        self.inv_listbox.pack(fill=tk.BOTH, expand=True)
        self.inv_listbox.configure(width=90)
        self.inv_listbox.bind('<<ListboxSelect>>', self.on_invoice_select)

        btn_frame = tk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        self.pay_button = tk.Button(btn_frame, text="Segna come Pagata", command=self.pay_invoice)
        self.pay_button.pack(side=tk.LEFT, padx=(0, 5))
        self.reminder_button = tk.Button(btn_frame, text="Invia Promemoria", command=self.remind_invoice)
        self.reminder_button.pack(side=tk.LEFT)

        # >>> forza testo nero quando disabilitati
        self.pay_button.configure(disabledforeground="#000000")
        self.reminder_button.configure(disabledforeground="#000000")
        # <<<

        create_frame = tk.LabelFrame(self, text="Nuova Fattura")
        create_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=10, pady=10)
        create_frame.pack_propagate(False)
        create_frame.configure(width=360)

        tk.Label(create_frame, text="Appuntamento:").grid(row=0, column=0, sticky=tk.W)
        self.app_var = tk.StringVar()
        self.app_combo = ttk.Combobox(create_frame, textvariable=self.app_var, state="readonly", width=75)
        self.app_combo.grid(row=0, column=1, sticky=tk.W)

        tk.Label(create_frame, text="Importo (€):").grid(row=1, column=0, sticky=tk.W)
        self.amount_entry = tk.Entry(create_frame)
        self.amount_entry.grid(row=1, column=1, sticky=tk.W)

        btn_row = tk.Frame(create_frame)
        btn_row.grid(row=2, column=0, columnspan=2, pady=(5, 0))

        btn_create = tk.Button(btn_row, text="Crea Fattura", command=self.add_invoice)
        btn_create.pack(side=tk.LEFT, padx=6)

        btn_export = tk.Button(btn_row, text="Esporta", command=self.export_selected_invoice)
        btn_export.pack(side=tk.LEFT, padx=6)

        self.banner_label = tk.Label(
            create_frame,
            text="Completare la seduta prima di proseguire con la fatturazione",
            fg="black"
        )
        self.banner_label.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        self.update_appointment_options()
        self.refresh_list()

    @staticmethod
    def _user_map_by_id():
        return {u.id: u for u in User.load_all()}

    @staticmethod
    def _patient_map_by_id():
        return {p.id: f"{p.nome} {p.cognome}" for p in Patient.load_all()}

    def _filter_invoices_for_user(self, invoices):
        if self.current_user is None:
            return invoices
        ruolo = getattr(self.current_user, 'ruolo', None)
        if ruolo == 'amministratore':
            return invoices
        physio_id = getattr(self.current_user, 'id', None)
        if physio_id is None:
            return invoices
        app_ids = {a.id for a in Appointment.get_appointments(physio_id=physio_id)}
        return [inv for inv in invoices if inv.appointment_id in app_ids]

    def toggle_paid_view(self):
        self.show_paid_mode = not self.show_paid_mode
        self.toggle_btn.config(text="Torna a Da Pagare" if self.show_paid_mode else "Fatture Pagate")
        self.refresh_list()

    def update_appointment_options(self):
        apps = Appointment.load_all()
        apps.sort(key=lambda x: (x.data, x.ora))

        invoiced_app_ids = {inv.appointment_id for inv in Invoice.load_all()}

        patient_map = {p.id: f"{p.nome} {p.cognome}" for p in Patient.load_all()}
        users_by_id = {u.id: u for u in User.load_all()}

        self._app_display_to_id.clear()
        options = []
        for a in apps:
            pat_name = patient_map.get(a.patient_id) or f"ID {a.patient_id} (non trovato)"
            phys = users_by_id.get(a.physio_id)
            phys_name = phys.nome if phys else f"ID {a.physio_id} (non trovato)"

            if a.id in invoiced_app_ids:
                tag = "[GIÀ FATTURATO]"
                ready = False
            elif a.stato != "completato":
                tag = "[NON COMPLETATO]"
                ready = False
            else:
                tag = "[PRONTO]"
                ready = True

            display = f"{a.data} {a.ora} — {pat_name} — {phys_name} — {tag}"
            self._app_display_to_id[display] = (a.id, a.id in invoiced_app_ids, ready)
            options.append(display)

        self.app_combo["values"] = options
        self.app_var.set(options[0] if options else "")

    def add_invoice(self):
        sel = self.app_var.get()
        if not sel:
            messagebox.showwarning("Selezione mancante", "Seleziona un appuntamento.")
            return

        data = self._app_display_to_id.get(sel)
        if not data:
            messagebox.showerror("Errore", "Appuntamento non trovato.")
            return

        app_id, is_invoiced, is_ready = data

        if is_invoiced:
            messagebox.showwarning(
                "Già fatturato",
                "Questo appuntamento risulta già fatturato. Non è possibile creare un'altra fattura."
            )
            return
        if not is_ready:
            apps = Appointment.get_appointments(id=app_id)
            stato = apps[0].stato if apps else "sconosciuto"
            messagebox.showwarning(
                "Seduta non completata",
                f"L'appuntamento selezionato risulta '{stato}'. "
                "Completa la seduta prima di procedere con la fatturazione."
            )
            return

        try:
            amount = float(self.amount_entry.get().replace(',', '.'))
        except ValueError:
            messagebox.showerror("Importo non valido", "Inserisci un numero valido.")
            return

        inv = invoice_controller.create_invoice_for_appointment(app_id, amount)
        if inv:
            messagebox.showinfo("Fattura Creata", f"Fattura #{inv.id} creata con successo.")
            self.amount_entry.delete(0, tk.END)
            self.update_appointment_options()
            self.refresh_list()
        else:
            messagebox.showerror("Errore", "Impossibile creare la fattura.")

    def refresh_list(self):
        self.inv_listbox.delete(0, tk.END)
        self._listbox_invoice_ids.clear()

        users_by_id = self._user_map_by_id()
        patient_map = self._patient_map_by_id()

        invoices = self._filter_invoices_for_user(Invoice.load_all())

        if self.show_paid_mode:
            invoices = [inv for inv in invoices if inv.stato_pagamento == 'pagata']
        else:
            invoices = [inv for inv in invoices if inv.stato_pagamento != 'pagata']

        for inv in invoices:
            apps = Appointment.get_appointments(id=inv.appointment_id)
            if not apps:
                display = f"(Visita mancante) — N/D — N/D — €{inv.importo:.2f} — " \
                          f"{'Pagata' if inv.stato_pagamento == 'pagata' else 'Da pagare'}"
                self.inv_listbox.insert(tk.END, display)
                self._listbox_invoice_ids.append(inv.id)
                continue

            app = apps[0]
            p_name = patient_map.get(app.patient_id, 'N/D')
            phys = users_by_id.get(app.physio_id)
            phys_name = phys.nome if phys else 'N/D'
            stato = "Pagata" if inv.stato_pagamento == 'pagata' else "Da pagare"

            display = f"{app.data} {app.ora} — {p_name} — {phys_name} — €{inv.importo:.2f} — {stato}"
            self.inv_listbox.insert(tk.END, display)
            self._listbox_invoice_ids.append(inv.id)

        if self.show_paid_mode:
            self.pay_button.config(state="disabled")
            self.reminder_button.config(state="disabled")
        else:
            self.pay_button.config(state="normal")
            self.reminder_button.config(state="normal")

        self.selected_inv_id = None

    def on_invoice_select(self, event=None):
        sel = self.inv_listbox.curselection()
        if not sel:
            self.selected_inv_id = None
            return
        idx = sel[0]
        if 0 <= idx < len(self._listbox_invoice_ids):
            self.selected_inv_id = self._listbox_invoice_ids[idx]
        else:
            self.selected_inv_id = None

    def pay_invoice(self):
        if not self.selected_inv_id:
            messagebox.showwarning("Selezione mancante", "Seleziona una fattura da segnare come pagata.")
            return
        ok = invoice_controller.mark_invoice_paid(self.selected_inv_id)
        if ok:
            messagebox.showinfo("Fattura Pagata", "La fattura è stata segnata come pagata.")
        else:
            messagebox.showerror("Errore", "Impossibile completare l'operazione.")
        self.refresh_list()

    def remind_invoice(self):
        if not self.selected_inv_id:
            messagebox.showwarning("Selezione mancante", "Seleziona una fattura.")
            return
        sent = invoice_controller.send_payment_reminder(self.selected_inv_id)
        if sent:
            messagebox.showinfo("Promemoria", "Promemoria di pagamento inviato.")
        else:
            messagebox.showwarning("Promemoria", "Operazione bloccata: fattura inesistente o già pagata.")
        self.refresh_list()

    def export_selected_invoice(self):
        if not self.selected_inv_id:
            messagebox.showwarning("Selezione mancante", "Seleziona una fattura da esportare.")
            return

        default_name = f"Fattura_{self.selected_inv_id}.txt"
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("File di testo", "*.txt")],
            title="Esporta fattura in TXT"
        )
        if not path:
            return

        ok = invoice_controller.export_invoice_txt(self.selected_inv_id, path)
        if ok:
            messagebox.showinfo("Esportazione completata", f"Fattura salvata in:\n{path}")
        else:
            messagebox.showerror("Errore", "Impossibile esportare la fattura.")
