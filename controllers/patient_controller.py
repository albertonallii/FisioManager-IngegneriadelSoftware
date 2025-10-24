from models.patient import Patient

def get_all_patients():
    return Patient.load_all()

def get_patient_by_id(pid):
    return Patient.get_by_id(pid, 1)

def add_new_patient(
    nome,
    cognome,
    codice_fiscale,
    email='',
    telefono='',
    note_cliniche='',
    peso=None,
    altezza=None,
):
    """
    Crea un nuovo paziente. 'peso' (kg) e 'altezza' (cm) sono opzionali.
    Le note sono 'note_cliniche'.
    """
    return Patient.create_patient(
        1, nome, cognome, codice_fiscale,
        email=email, telefono=telefono,
        note_cliniche=note_cliniche,
        peso=peso, altezza=altezza
    )

def update_patient_info(
    pid,
    nome=None,
    cognome=None,
    codice_fiscale=None,
    email=None,
    telefono=None,
    note_cliniche=None,
    peso=None,
    altezza=None,
):
    """Aggiorna i dati del paziente (solo i campi passati != None)."""
    return Patient.update_patient(
        pid, 1,
        nome=nome,
        cognome=cognome,
        codice_fiscale=codice_fiscale,
        email=email,
        telefono=telefono,
        note_cliniche=note_cliniche,
        peso=peso,
        altezza=altezza
    )

def search_patients(keyword):
    return Patient.search_patients(1, keyword)

def delete_patient(pid):
    success = Patient.delete_patient(pid)
    if not success:
        raise ValueError("Paziente non trovato.")
    return True
