from models import storage
from datetime import date

class Invoice:
    file_name = 'invoices.json'

    def __init__(self, id, appointment_id, data_emissione, importo,
                 stato_pagamento='non_pagata',
                 promemoria_inviato=False,
                 pagamento_notificato=False):   # <-- nuovo flag
        self.id = id
        self.appointment_id = appointment_id
        self.data_emissione = data_emissione if isinstance(data_emissione, str) else data_emissione.isoformat()
        self.importo = importo
        self.stato_pagamento = stato_pagamento
        self.promemoria_inviato = promemoria_inviato
        self.pagamento_notificato = pagamento_notificato  # <-- nuovo

    def to_dict(self):
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "data_emissione": self.data_emissione,
            "importo": self.importo,
            "stato_pagamento": self.stato_pagamento,
            "promemoria_inviato": self.promemoria_inviato,
            "pagamento_notificato": self.pagamento_notificato  # <-- nuovo
        }

    @classmethod
    def load_all(cls):
        return [cls(**item) for item in storage.load_data(cls.file_name)]

    @classmethod
    def save_all(cls, invs):
        storage.save_data(cls.file_name, [i.to_dict() for i in invs])

    @classmethod
    def create_invoice(cls, appointment_id, importo, data_emissione=None):
        invs = cls.load_all()
        new_id = max([i.id for i in invs], default=0) + 1
        inv = cls(new_id, appointment_id, data_emissione or date.today(), importo)
        invs.append(inv)
        cls.save_all(invs)
        return inv

    @classmethod
    def get_invoice(cls, inv_id):
        for inv in storage.load_data(cls.file_name):
            if inv["id"] == inv_id:
                return inv
        return None

    @classmethod
    def mark_invoice_paid(cls, inv_id):
        invs = cls.load_all()
        for inv in invs:
            if inv.id == inv_id:
                inv.stato_pagamento = 'pagata'
                break
        cls.save_all(invs)

    @classmethod
    def mark_payment_reminder_sent(cls, inv_id):
        invs = cls.load_all()
        for inv in invs:
            if inv.id == inv_id:
                inv.promemoria_inviato = True
                break
        cls.save_all(invs)
        return True

    @classmethod
    def mark_payment_notified(cls, inv_id):
        invs = cls.load_all()
        for inv in invs:
            if inv.id == inv_id:
                inv.pagamento_notificato = True
                break
        cls.save_all(invs)
        return True
