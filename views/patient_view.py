import tkinter as tk
from tkinter import messagebox, filedialog
import theme_fisio
from controllers import patient_controller
from models.appointment import Appointment
try:from models.plan import TreatmentPlan
except Exception:TreatmentPlan = None

class PatientWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        theme_fisio.paint(self)
        self.title("Gestione Pazienti")
        self.geometry("920x560")
        self.selected_patient_id = None

        left_frame = tk.Frame(self)
        left_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        tk.Label(left_frame, text="Cerca:").pack(anchor="w")

        search_row = tk.Frame(left_frame)
        search_row.pack(fill="x", pady=(2, 6))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_row, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_patient())

        tk.Button(search_row, text="Cerca", command=self.search_patient).pack(side="left", padx=4)
        tk.Button(search_row, text="Pulisci", command=self.clear_search).pack(side="left")

        self.patient_listbox = tk.Listbox(left_frame, exportselection=False)
        self.patient_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=self.patient_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.patient_listbox.config(yscrollcommand=scrollbar.set)
        self.patient_listbox.bind("<<ListboxSelect>>", self.on_select)

        self.no_results_label = tk.Label(left_frame, text="Nessun paziente trovato.", fg="red")

        right_frame = tk.LabelFrame(self, text="Fascicolo paziente")
        right_frame.pack(side="right", fill="y", padx=10, pady=8)

        row = 0

        def add_row(label_text, widget):
            nonlocal row
            tk.Label(right_frame, text=label_text).grid(row=row, column=0, sticky="e", pady=2, padx=(0, 6))
            widget.grid(row=row, column=1, pady=2, sticky="w")
            row += 1

        self.nome_entry = tk.Entry(right_frame, width=28)
        add_row("Nome", self.nome_entry)

        self.cognome_entry = tk.Entry(right_frame, width=28)
        add_row("Cognome", self.cognome_entry)

        self.cf_entry = tk.Entry(right_frame, width=28)
        add_row("Codice Fiscale", self.cf_entry)

        self.email_entry = tk.Entry(right_frame, width=28)
        add_row("Email", self.email_entry)

        self.tel_entry = tk.Entry(right_frame, width=28)
        add_row("Telefono", self.tel_entry)

        self.peso_entry = tk.Entry(right_frame, width=12)
        add_row("Peso (kg)", self.peso_entry)

        self.altezza_entry = tk.Entry(right_frame, width=12)
        add_row("Altezza (cm)", self.altezza_entry)

        tk.Label(right_frame, text="Note cliniche").grid(row=row, column=0, sticky="ne", pady=2, padx=(0, 6))
        self.note_text = tk.Text(right_frame, width=46, height=6, wrap="word")
        self.note_text.grid(row=row, column=1, pady=2, sticky="w")
        row += 1

        btns = tk.Frame(right_frame)
        btns.grid(row=row, column=0, columnspan=2, pady=10, sticky="w")
        tk.Button(btns, text="Nuovo", command=lambda: self.clear_form(keep_search=True)).pack(side="left", padx=4)
        self.add_btn = tk.Button(btns, text="Aggiungi", command=self.add_patient)
        self.add_btn.pack(side="left", padx=4)
        self.update_btn = tk.Button(btns, text="Salva modifiche", command=self.update_patient, state="disabled")
        self.update_btn.pack(side="left", padx=4)
        self.delete_btn = tk.Button(btns, text="Elimina", command=self.delete_patient, state="disabled")
        self.delete_btn.pack(side="left", padx=4)
        tk.Button(btns, text="Scarica fascicolo", command=self.download_patient_dossier).pack(side="left", padx=4)

        # testo nero quando disabilitati
        self.update_btn.configure(disabledforeground="#000000")
        self.delete_btn.configure(disabledforeground="#000000")

        self.refresh_list()

    def _fmt_row(self, p):
        peso = f"{p.peso:.1f}kg" if isinstance(p.peso, (int, float)) else "N/D"
        alt = f"{p.altezza:.0f}cm" if isinstance(p.altezza, (int, float)) else "N/D"
        cf = p.codice_fiscale or "N/D"
        return f"{p.id} — {p.nome} {p.cognome} — CF:{cf} — {peso} / {alt}"

    def _parse_float_or_none(self, s: str):
        s = (s or "").strip().replace(",", ".")
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None

    def refresh_list(self):
        self.no_results_label.pack_forget()
        patients = patient_controller.get_all_patients()
        patients.sort(key=lambda p: p.id)
        self.patient_listbox.delete(0, tk.END)
        for p in patients:
            self.patient_listbox.insert(tk.END, self._fmt_row(p))
        self.clear_form(keep_search=True)

    def search_patient(self):
        q = (self.search_var.get() or "").strip().lower()
        if not q:
            self.refresh_list()
            return
        patients = patient_controller.get_all_patients()
        filtered = [
            p for p in patients
            if q in p.nome.lower()
            or q in p.cognome.lower()
            or q in (p.codice_fiscale or "").lower()
        ]
        self.patient_listbox.delete(0, tk.END)
        if not filtered:
            self.no_results_label.pack(anchor="w")
            return
        self.no_results_label.pack_forget()
        for p in filtered:
            self.patient_listbox.insert(tk.END, self._fmt_row(p))

    def clear_search(self):
        self.refresh_list()

    def on_select(self, event):
        self.no_results_label.pack_forget()
        sel = self.patient_listbox.curselection()
        if not sel:
            return
        row_text = self.patient_listbox.get(sel[0]).strip()
        try:
            pid = int(row_text.split()[0])
        except Exception:
            return
        pat = patient_controller.get_patient_by_id(pid)
        if not pat:
            return

        self.selected_patient_id = pid

        self.nome_entry.delete(0, tk.END); self.nome_entry.insert(0, pat.nome)
        self.cognome_entry.delete(0, tk.END); self.cognome_entry.insert(0, pat.cognome)
        self.cf_entry.delete(0, tk.END); self.cf_entry.insert(0, pat.codice_fiscale)
        self.email_entry.delete(0, tk.END); self.email_entry.insert(0, pat.email)
        self.tel_entry.delete(0, tk.END); self.tel_entry.insert(0, pat.telefono)
        self.peso_entry.delete(0, tk.END); self.peso_entry.insert(0, "" if pat.peso in (None, "") else pat.peso)
        self.altezza_entry.delete(0, tk.END); self.altezza_entry.insert(0, "" if pat.altezza in (None, "") else pat.altezza)
        self.note_text.delete("1.0", "end"); self.note_text.insert("1.0", getattr(pat, "note_cliniche", "") or "")

        self.add_btn.config(state="disabled")
        # >>> forza il colore del testo quando abilitati
        self.update_btn.config(state="normal", fg="white")
        self.delete_btn.config(state="normal", fg="white")

    def clear_form(self, keep_search=False):
        for e in (self.nome_entry, self.cognome_entry, self.cf_entry,
                  self.email_entry, self.tel_entry, self.peso_entry, self.altezza_entry):
            e.delete(0, tk.END)
        self.note_text.delete("1.0", "end")
        self.patient_listbox.selection_clear(0, tk.END)
        self.selected_patient_id = None
        # tornano disabilitati (testo nero grazie a disabledforeground)
        self.update_btn.config(state="disabled")
        self.add_btn.config(state="normal")
        self.delete_btn.config(state="disabled")
        self.no_results_label.pack_forget()
        if not keep_search:
            self.search_var.set('')

    def add_patient(self):
        nome = self.nome_entry.get().strip()
        cognome = self.cognome_entry.get().strip()
        cf = self.cf_entry.get().strip()
        email = self.email_entry.get().strip()
        tel = self.tel_entry.get().strip()
        peso = self._parse_float_or_none(self.peso_entry.get())
        altezza = self._parse_float_or_none(self.altezza_entry.get())
        note_cliniche = self.note_text.get("1.0", "end-1c").strip()

        if not nome or not cognome or not cf:
            messagebox.showwarning("Campi obbligatori", "Nome, Cognome e Codice Fiscale sono obbligatori.")
            return
        if tel and not tel.isdigit():
            messagebox.showerror("Errore", "Il telefono deve contenere solo cifre.")
            return
        if email and ("@" not in email or "." not in email[email.index("@"):]):
            messagebox.showerror("Errore", "Email non valida.")
            return

        p = patient_controller.add_new_patient(
            nome, cognome, cf,
            email=email, telefono=tel,
            note_cliniche=note_cliniche,
            peso=peso, altezza=altezza
        )
        if p is None:
            messagebox.showerror("Errore", "Codice fiscale già presente.")
            return

        messagebox.showinfo("Successo", "Paziente aggiunto.")
        self.clear_form()
        self.refresh_list()

    def update_patient(self):
        if not self.selected_patient_id:
            messagebox.showwarning("Selezione mancante", "Seleziona un paziente.")
            return
        nome = self.nome_entry.get().strip()
        cognome = self.cognome_entry.get().strip()
        cf = self.cf_entry.get().strip()
        email = self.email_entry.get().strip()
        tel = self.tel_entry.get().strip()
        peso = self._parse_float_or_none(self.peso_entry.get())
        altezza = self._parse_float_or_none(self.altezza_entry.get())
        note_cliniche = self.note_text.get("1.0", "end-1c").strip()

        if not nome or not cognome or not cf:
            messagebox.showwarning("Campi obbligatori", "Nome, Cognome e CF obbligatori.")
            return

        if tel and not tel.isdigit():
            messagebox.showerror("Errore", "Telefono: solo cifre.")
            return
        if email and ("@" not in email or "." not in email[email.index("@"):]):
            messagebox.showerror("Errore", "Email non valida.")
            return

        ok = patient_controller.update_patient_info(
            self.selected_patient_id,
            nome=nome, cognome=cognome, codice_fiscale=cf,
            email=email, telefono=tel,
            peso=peso, altezza=altezza,
            note_cliniche=note_cliniche
        )
        if not ok:
            messagebox.showerror("Errore", "Aggiornamento fallito.")
        else:
            messagebox.showinfo("Successo", "Paziente aggiornato.")
        self.clear_form()
        self.refresh_list()

    def delete_patient(self):
        if not self.selected_patient_id:
            messagebox.showwarning("Selezione mancante", "Seleziona un paziente da eliminare.")
            return
        if not messagebox.askyesno("Conferma Eliminazione", "Eliminare definitivamente il paziente selezionato?"):
            return
        patient_controller.delete_patient(self.selected_patient_id)
        messagebox.showinfo("Eliminato", "Paziente eliminato con successo.")
        self.clear_form()
        self.refresh_list()

    def download_patient_dossier(self):
        if not self.selected_patient_id:
            messagebox.showwarning("Selezione mancante", "Seleziona un paziente.")
            return

        pat = patient_controller.get_patient_by_id(self.selected_patient_id)
        if not pat:
            messagebox.showerror("Errore", "Paziente non trovato.")
            return

        apps = [a for a in Appointment.load_all() if a.patient_id == self.selected_patient_id]
        apps.sort(key=lambda a: (a.data, a.ora))
        session_notes = [
            f"- {a.data} {a.ora}: {str(a.note_cliniche).strip()}"
            for a in apps
            if getattr(a, "note_cliniche", None) and str(a.note_cliniche).strip()
        ]

        notes = []
        if getattr(pat, "note_cliniche", None) and str(pat.note_cliniche).strip():
            notes.append(f"- {str(pat.note_cliniche).strip()}")
        notes.extend(session_notes)

        plans_lines = []
        try:
            all_plans = TreatmentPlan.load_all() if TreatmentPlan else []
            patient_plans = [pl for pl in all_plans if getattr(pl, "patient_id", None) == self.selected_patient_id]
            patient_plans.sort(key=lambda pl: getattr(pl, "id", 0))
            for pl in patient_plans:
                status = "Completato" if getattr(pl, "completato", False) else "Attivo"
                descr = getattr(pl, "descrizione", "—")
                plans_lines.append(f"- [{status}] {descr}")
        except Exception:
            plans_lines.append("N/D (modulo piani non disponibile)")

        peso_str = f"{pat.peso} kg" if pat.peso not in (None, "") else "N/D"
        alt_str = f"{pat.altezza} cm" if pat.altezza not in (None, "") else "N/D"

        lines = [
            "==============================\n",
            "        FASCICOLO PAZIENTE     \n",
            "==============================\n",
            f"ID Paziente : {pat.id}\n",
            f"Nome        : {pat.nome}\n",
            f"Cognome     : {pat.cognome}\n",
            f"Cod. Fiscale: {pat.codice_fiscale}\n",
            f"Email       : {pat.email or 'N/D'}\n",
            f"Telefono    : {pat.telefono or 'N/D'}\n",
            f"Peso        : {peso_str}\n",
            f"Altezza     : {alt_str}\n",
            "\n---- NOTE CLINICHE ----\n",
        ]
        if notes:
            lines.extend(n + "\n" for n in notes)
        else:
            lines.append("Nessuna nota clinica disponibile.\n")

        lines.append("\n---- PIANI DI TRATTAMENTO ----\n")
        if plans_lines:
            lines.extend(p + "\n" for p in plans_lines)
        else:
            lines.append("Nessun piano di trattamento.\n")

        default_name = f"Fascicolo_{pat.cognome}_{pat.nome}.txt".replace(" ", "_")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("File di testo", "*.txt")],
            title="Salva Fascicolo Paziente"
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(lines)
            messagebox.showinfo("Fascicolo Salvato", f"Report salvato in:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Errore Salvataggio", f"Impossibile scrivere il file:\n{e}")
