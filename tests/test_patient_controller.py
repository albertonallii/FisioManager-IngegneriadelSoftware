import controllers.patient_controller as pc
from models.patient import Patient

def test_add_and_search_patient(temp_data_dir):
    pat = pc.add_new_patient(
        nome="Mario",
        cognome="Rossi",
        codice_fiscale="RSSMRA90A01F205X",
        email="mario@email.it",
        telefono="3331234567"
    )
    assert isinstance(pat, Patient)
    assert hasattr(pat, "id")
    pid = pat.id
    loaded = next((p for p in Patient.load_all() if p.id == pid), None)
    assert loaded is not None
    assert loaded.nome == "Mario"
    results = pc.search_patients("Mario")
    assert any(r.nome == "Mario" or "Mario" in getattr(r, "nome", "") for r in results)
