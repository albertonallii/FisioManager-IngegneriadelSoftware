import controllers.invoice_controller as ic
from models.invoice import Invoice

def test_create_and_mark_invoice(temp_data_dir):
    inv = ic.create_invoice_for_appointment(1, 50.0)
    assert isinstance(inv, Invoice)
    assert hasattr(inv, "id")
    iid = inv.id
    ok = ic.mark_invoice_paid(iid)
    assert ok is True
    data = [i for i in Invoice.load_all() if i.id == iid]
    assert len(data) == 1
    stato = getattr(data[0], "stato_pagamento", None)
    assert stato in ("pagata", "Pagata", "paid", True)
