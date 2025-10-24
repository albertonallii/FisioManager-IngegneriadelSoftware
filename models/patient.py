from models import storage

class Patient:
    file_name = 'patients.json'

    def __init__(
        self,
        id,
        owner_id,
        nome,
        cognome,
        codice_fiscale,
        email='',
        telefono='',
        peso=None,
        altezza=None,
        note_cliniche='',
    ):
        self.id = id
        self.owner_id = owner_id
        self.nome = nome
        self.cognome = cognome
        self.codice_fiscale = codice_fiscale
        self.email = email
        self.telefono = telefono
        self.peso = peso
        self.altezza = altezza
        self.note_cliniche = note_cliniche

    def to_dict(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "nome": self.nome,
            "cognome": self.cognome,
            "codice_fiscale": self.codice_fiscale,
            "email": self.email,
            "telefono": self.telefono,
            "peso": self.peso,
            "altezza": self.altezza,
            "note_cliniche": self.note_cliniche,
        }

    @classmethod
    def _coerce_legacy(cls, item: dict) -> dict:
        fixed = dict(item)
        if "note_cliniche" not in fixed:
            fixed["note_cliniche"] = fixed.get("note", "")
        if "note" in fixed:
            fixed.pop("note", None)

        fixed.setdefault("peso", None)
        fixed.setdefault("altezza", None)

        return fixed

    @classmethod
    def load_all(cls):
        data = storage.load_data(cls.file_name)
        objs = []
        for raw in data:
            r = cls._coerce_legacy(raw)
            obj = cls(
                r.get("id"),
                r.get("owner_id"),
                r.get("nome"),
                r.get("cognome"),
                r.get("codice_fiscale"),
                r.get("email", ""),
                r.get("telefono", ""),
                peso=r.get("peso"),
                altezza=r.get("altezza"),
                note_cliniche=r.get("note_cliniche", ""),
            )
            objs.append(obj)
        return objs

    @classmethod
    def get_all_for_owner(cls, owner_id):
        return [p for p in cls.load_all() if p.owner_id == owner_id]

    @classmethod
    def get_by_id(cls, pid, owner_id):
        for p in cls.load_all():
            if p.id == pid and p.owner_id == owner_id:
                return p
        return None

    @classmethod
    def create_patient(
        cls,
        owner_id,
        nome,
        cognome,
        codice_fiscale,
        email='',
        telefono='',
        note_cliniche='',
        peso=None,
        altezza=None,
    ):
        patients = cls.load_all()
        new_id = max([p.id for p in patients], default=0) + 1
        pat = cls(
            new_id, owner_id, nome, cognome, codice_fiscale,
            email=email, telefono=telefono,
            peso=peso, altezza=altezza, note_cliniche=note_cliniche
        )
        patients.append(pat)
        cls.save_all(patients)
        return pat

    @classmethod
    def update_patient(cls, pid, owner_id, **kwargs):
        patients = cls.load_all()
        updated = False
        for p in patients:
            if p.id == pid and p.owner_id == owner_id:
                for k, v in kwargs.items():
                    if v is not None and hasattr(p, k):
                        setattr(p, k, v)
                        updated = True
                break
        if updated:
            cls.save_all(patients)
        return updated

    @classmethod
    def delete_patient(cls, pid):
        patients = cls.load_all()
        new_list = [p for p in patients if p.id != pid]
        if len(new_list) == len(patients):
            return False
        cls.save_all(new_list)
        return True

    @classmethod
    def search_patients(cls, owner_id, keyword):
        kw = (keyword or "").lower()
        return [
            p for p in cls.get_all_for_owner(owner_id)
            if kw in p.nome.lower()
            or kw in p.cognome.lower()
            or kw in p.codice_fiscale.lower()
        ]

    @classmethod
    def save_all(cls, patients_list):
        data = [p.to_dict() for p in patients_list]
        storage.save_data(cls.file_name, data)
