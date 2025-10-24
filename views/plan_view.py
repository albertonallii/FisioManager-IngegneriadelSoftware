import tkinter as tk
from tkinter import ttk, messagebox
from controllers import plan_controller, patient_controller
import theme_fisio

class PlanWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        theme_fisio.paint(self)
        self.title("Piani di Trattamento")
        self.geometry("800x500")
        self.selected_plan_id = None

        self._patient_label_to_id = {}
        self._patient_id_to_label = {}

        list_frame = tk.Frame(self)
        list_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        tk.Label(list_frame, text="Elenco Piani:").pack(anchor="w")

        self.plan_listbox = tk.Listbox(list_frame)
        self.plan_listbox.config(bg="white", fg="black")
        self.plan_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.plan_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.plan_listbox.config(yscrollcommand=scrollbar.set)

        self.plan_listbox.bind("<<ListboxSelect>>", self.on_select)

        form_frame = tk.LabelFrame(self, text="Dettagli / Modifica piano")
        form_frame.pack(side="left", fill="y", padx=10, pady=8)
        form_frame.grid_columnconfigure(1, weight=1)

        r = 0
        tk.Label(form_frame, text="Paziente:").grid(row=r, column=0, sticky="e", pady=2)
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(form_frame, textvariable=self.patient_var, state="readonly", width=32)
        self.patient_combo.grid(row=r, column=1, sticky="we", pady=2)

        r += 1
        tk.Label(form_frame, text="Descrizione:").grid(row=r, column=0, sticky="e", pady=2)
        self.desc_entry = tk.Entry(form_frame, bg="white", fg="black", width=40)
        self.desc_entry.grid(row=r, column=1, sticky="we", pady=2)
        self.desc_entry.configure(borderwidth=1, relief="solid")

        r += 1
        btns = tk.Frame(form_frame)
        btns.grid(row=r, column=0, columnspan=2, pady=8)

        tk.Button(btns, text="Aggiungi", command=self.add_plan).pack(side="left", padx=5)

        self.update_btn = tk.Button(btns, text="Aggiorna", command=self.update_plan, state="disabled")
        self.update_btn.pack(side="left", padx=5)
        self.update_btn.configure(disabledforeground="#000000")  # testo nero quando disabilitato

        self.complete_btn = tk.Button(btns, text="Completa", command=self.complete_plan, state="disabled")
        self.complete_btn.pack(side="left", padx=5)
        self.complete_btn.configure(disabledforeground="#000000")

        self.delete_btn = tk.Button(btns, text="Elimina", command=self.delete_plan, state="disabled")
        self.delete_btn.pack(side="left", padx=5)
        self.delete_btn.configure(disabledforeground="#000000")

        self._load_patients_into_combo()
        self.refresh_list()

        style = ttk.Style(self)
        try:
            style.theme_use('default')
        except Exception:
            pass
        style.configure('TCombobox', foreground='black', fieldbackground='white')

    def _load_patients_into_combo(self):
        patients = patient_controller.get_all_patients()
        patients.sort(key=lambda p: (p.cognome.lower(), p.nome.lower()))
        labels = []
        self._patient_label_to_id.clear()
        self._patient_id_to_label.clear()
        for p in patients:
            label = f"{p.id}: {p.nome} {p.cognome}"
            self._patient_label_to_id[label] = p.id
            self._patient_id_to_label[p.id] = label
            labels.append(label)
        self.patient_combo["values"] = labels

    def refresh_list(self):
        plans = plan_controller.get_all_plans()
        plans.sort(key=lambda pl: pl.id)
        self.plan_listbox.delete(0, tk.END)

        patients = {p.id: f"{p.nome} {p.cognome}" for p in patient_controller.get_all_patients()}

        for pl in plans:
            pat_name = patients.get(pl.patient_id, f"ID {pl.patient_id}")
            status = "Completato" if getattr(pl, 'completato', False) else "Attivo"
            descr = getattr(pl, 'descrizione', '')
            self.plan_listbox.insert(tk.END, f"{pl.id}: {pat_name} - {descr} ({status})")

        self.selected_plan_id = None
        self.update_btn.config(state="disabled")
        self.complete_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
        # quando disabilitati, il testo resta nero grazie a disabledforeground

        self.patient_combo.set('')
        self.desc_entry.delete(0, tk.END)

    def _get_selected_plan(self):
        sel = self.plan_listbox.curselection()
        if not sel:
            return None
        item_text = self.plan_listbox.get(sel[0])
        try:
            plan_id = int(item_text.split(":")[0])
        except Exception:
            return None
        plans = plan_controller.get_all_plans()
        return next((p for p in plans if p.id == plan_id), None)

    def on_select(self, _event=None):
        pl = self._get_selected_plan()
        if not pl:
            self.selected_plan_id = None
            self.update_btn.config(state="disabled")
            self.complete_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            return

        self.selected_plan_id = pl.id

        label = self._patient_id_to_label.get(pl.patient_id, '')
        self.patient_combo.set(label)
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, getattr(pl, 'descrizione', ''))

        # abilitando, forzo il testo bianco (coerente con il tema)
        self.update_btn.config(state="normal", fg="white")
        self.delete_btn.config(state="normal", fg="white")
        if getattr(pl, 'completato', False):
            self.complete_btn.config(state="disabled")
        else:
            self.complete_btn.config(state="normal", fg="white")

    def add_plan(self):
        if not self.patient_var_valid() or not self.description_valid():
            return
        pid = self._patient_label_to_id[self.patient_var.get()]
        desc = self.desc_entry.get().strip()

        plan = plan_controller.create_treatment_plan(pid, desc)
        if not plan:
            messagebox.showerror("Errore", "Impossibile creare il piano.")
        else:
            messagebox.showinfo("Successo", "Piano di trattamento aggiunto.")
            self.patient_combo.set('')
            self.desc_entry.delete(0, tk.END)
        self.refresh_list()

    def update_plan(self):
        "Aggiorna il piano selezionato (paziente e descrizione)."
        if not self.selected_plan_id:
            messagebox.showwarning("Selezione mancante", "Seleziona un piano dall'elenco.")
            return

        if not self.patient_var.get():
            messagebox.showwarning("Campi obbligatori", "Seleziona un paziente.")
            return
        if self.patient_var.get() not in self._patient_label_to_id:
            messagebox.showerror("Errore", "Selezione paziente non valida.")
            return
        desc = self.desc_entry.get().strip()
        if not desc:
            messagebox.showwarning("Campi obbligatori", "Inserisci una descrizione per il piano.")
            return

        pid = self._patient_label_to_id[self.patient_var.get()]

        ok = plan_controller.update_treatment_plan(self.selected_plan_id, pid, desc)
        if not ok:
            messagebox.showerror("Errore", "Impossibile aggiornare il piano (ID non trovato).")
            return

        messagebox.showinfo("Aggiornato", "Piano aggiornato correttamente.")
        self.refresh_list()

    def complete_plan(self):
        if not self.selected_plan_id:
            messagebox.showwarning("Selezione mancante", "Seleziona un piano da completare.")
            return
        plan_controller.complete_treatment_plan(self.selected_plan_id)
        messagebox.showinfo("Piano Completato", "Il piano è stato segnato come completato.")
        self.refresh_list()

    def delete_plan(self):
        if not self.selected_plan_id:
            messagebox.showwarning("Selezione mancante", "Seleziona un piano da eliminare.")
            return
        if not messagebox.askyesno("Conferma", "Eliminare definitivamente il piano selezionato?"):
            return

        ok = plan_controller.delete_treatment_plan(self.selected_plan_id)
        if not ok:
            messagebox.showerror("Errore", "Impossibile eliminare il piano.")
            return

        messagebox.showinfo("Eliminato", "Piano eliminato.")
        self.refresh_list()

    def patient_var_valid(self):
        if not self.patient_var.get():
            messagebox.showwarning("Campi obbligatori", "Seleziona un paziente.")
            return False
        if self.patient_var.get() not in self._patient_label_to_id:
            messagebox.showerror("Errore", "Selezione paziente non valida.")
            return False
        return True

    def description_valid(self):
        desc = self.desc_entry.get().strip()
        if not desc:
            messagebox.showwarning("Campi obbligatori", "Inserisci una descrizione per il piano.")
            return False
        return True
