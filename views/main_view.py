import tkinter as tk
from tkinter import messagebox
from models.patient import Patient
from models.appointment import Appointment
from models.invoice import Invoice
from views import patient_view, appointment_view, invoice_view, plan_view, user_view
import theme_fisio

class MainWindow:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title('FisioManager - Dashboard')
        self.root.geometry('400x400')

        theme_fisio.apply_theme(self.root)
        theme_fisio.paint(self.root)

        tk.Label(self.root, text=f'Benvenuto, {user.nome}!').pack(pady=10)
        tk.Button(self.root, text='Gestione Pazienti', width=20, command=self.open_patients).pack(pady=5)
        tk.Button(self.root, text='Gestione Agenda', width=20, command=self.open_appointments).pack(pady=5)
        tk.Button(self.root, text='Fatture e Pagamenti', width=20, command=self.open_invoices).pack(pady=5)
        tk.Button(self.root, text='Piani di Trattamento', width=20, command=self.open_plans).pack(pady=5)
        if self.user.ruolo == 'amministratore':
            tk.Button(self.root, text='Gestione Utenti', width=20, command=self.open_users).pack(pady=5)
        tk.Button(self.root, text='Genera Report', width=20, command=self.generate_report).pack(pady=5)
        tk.Button(self.root, text='Esci', width=20, command=self.root.destroy).pack(pady=20)

        self.root.mainloop()

    def open_patients(self):
        patient_view.PatientWindow(self.root)

    def open_appointments(self):
        appointment_view.AppointmentWindow(self.root, self.user)

    def open_invoices(self):
        invoice_view.InvoiceWindow(self.root)

    def open_plans(self):
        plan_view.PlanWindow(self.root)

    def open_users(self):
        user_view.UserWindow(self.root)

    def generate_report(self):
        total_patients = len(Patient.load_all())
        apps = Appointment.load_all()
        if self.user.ruolo != 'amministratore':
            apps = [a for a in apps if a.physio_id == self.user.id]
        completed = len([a for a in apps if a.stato == 'completato'])
        annullati = len([a for a in apps if a.stato == 'annullato'])
        programmati = len([a for a in apps if a.stato == 'programmato'])
        invoices = Invoice.load_all()
        if self.user.ruolo != 'amministratore':
            physio_ids = {a.id for a in apps}
            invoices = [i for i in invoices if i.appointment_id in physio_ids]
        paid = len([i for i in invoices if i.stato_pagamento == 'pagata'])
        unpaid = len(invoices) - paid
        incasso = sum(i.importo for i in invoices if i.stato_pagamento == 'pagata')
        msg = (f"Pazienti totali: {total_patients}\n"
               f"Appuntamenti completati: {completed}\n"
               f"Appuntamenti annullati: {annullati}\n"
               f"Appuntamenti programmati: {programmati}\n"
               f"Fatture pagate: {paid}\n"
               f"Fatture non pagate: {unpaid}\n"
               f"Incasso: €{incasso:.2f}")
        messagebox.showinfo('Report', msg)
