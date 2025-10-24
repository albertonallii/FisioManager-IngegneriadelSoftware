from models.invoice import Invoice
from models.appointment import Appointment
from models.patient import Patient
from datetime import date

def get_invoices_for_user(user=None):
    invs = Invoice.load_all()
    if user is None:
        return invs
    if getattr(user, "ruolo", None) == "amministratore":
        return invs
    uid = getattr(user, "id", None)
    if uid is None:
        return invs
    physio_apps = {a.id for a in Appointment.get_appointments(physio_id=uid)}
    return [inv for inv in invs if inv.appointment_id in physio_apps]

def create_invoice_for_appointment(app_id, importo):
    return Invoice.create_invoice(app_id, importo, date.today())

def mark_invoice_paid(inv_id):
    inv = Invoice.get_invoice(inv_id)
    if not inv:
        return False
    Invoice.mark_invoice_paid(inv_id)
    return True

def send_payment_reminder(inv_id):
    inv = Invoice.get_invoice(inv_id)
    if not inv:
        return False
    if inv.get("stato_pagamento") == "pagata":
        return False
    return Invoice.mark_payment_reminder_sent(inv_id)

def export_invoice_txt(inv_id, out_path=None):
    COMPANY_NAME    = "FisioManager SPA"
    COMPANY_TAGLINE = "Studio di Fisioterapia"
    COMPANY_ADDRESS = "Via Brecce Bianche, 12"
    COMPANY_VAT     = "0000000001"
    SEPARATOR       = "=============================="

    inv = Invoice.get_invoice(inv_id)  # dict
    if not inv:
        return None

    apps = Appointment.get_appointments(id=inv["appointment_id"])
    app = apps[0] if apps else None

    pat_name = "N/D"
    pat_cf   = ""
    phys_name = "N/D"

    if app:
        pat = Patient.get_by_id(app.patient_id, 1)
        if pat:
            pat_name = f"{pat.nome} {pat.cognome}"
            pat_cf   = pat.codice_fiscale or ""
        try:
            from models.user import User
            phys = next((u for u in User.load_all() if u.id == app.physio_id), None)
            if phys:
                phys_name = phys.nome
        except Exception:
            pass

    visita_data = app.data if app else "N/D"
    visita_ora  = app.ora  if app else "N/D"

    lines = [
        f"{SEPARATOR}\n",
        f"{COMPANY_NAME}\n",
        f"{COMPANY_TAGLINE}\n",
        f"{COMPANY_ADDRESS}\n",
        f"P.IVA e C.F. : {COMPANY_VAT}\n",
        f"{SEPARATOR}\n",
        "\n",
        f"Fattura n{inv_id}\n",
        f"Data Emissione: {inv['data_emissione']}\n",
        f"Paziente    : {pat_name}{('—' + pat_cf) if pat_cf else ''}\n",
        f"Fisioterapista: {phys_name}\n",
        f"Visita      : {visita_data} ore {visita_ora}\n",
        f"Importo     : €{inv['importo']}\n",
        f"Stato       : {inv['stato_pagamento']}\n",
        "\n",
        "Grazie per averci scelto.\n",
    ]

    if not out_path:
        out_path = f"Fattura_{inv_id}.txt"
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return out_path
    except Exception:
        return None

