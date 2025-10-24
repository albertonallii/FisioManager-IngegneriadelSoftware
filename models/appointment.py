from models import storage
import datetime

class Appointment:
    file_name = 'appointments.json'

    def __init__(self, id, patient_id, physio_id, data, ora,
                 trattamento='', stato='programmato',
                 note_cliniche='', promemoria_inviato=False):
        self.id = id
        self.patient_id = patient_id
        self.physio_id = physio_id
        self.data = data
        self.ora = ora
        self.trattamento = trattamento
        self.stato = stato
        self.note_cliniche = note_cliniche
        self.promemoria_inviato = promemoria_inviato

    def to_dict(self):
        return self.__dict__

    @classmethod
    def load_all(cls):

        return [cls(**item) for item in storage.load_data(cls.file_name)]

    @classmethod
    def save_all(cls, apps):
        storage.save_data(cls.file_name, [a.to_dict() for a in apps])

    @classmethod
    def create_appointment(cls, patient_id, physio_id, data, ora, trattamento=''):
        apps = cls.load_all()
        new_dt = datetime.datetime.strptime(f"{data} {ora}", "%Y-%m-%d %H:%M")
        durata = datetime.timedelta(hours=1)

        for a in apps:
            if a.physio_id == physio_id and a.data == data and a.stato == 'programmato':
                existing_dt = datetime.datetime.strptime(f"{a.data} {a.ora}", "%Y-%m-%d %H:%M")
                if new_dt < existing_dt + durata and existing_dt < new_dt + durata:
                    raise ValueError(
                        f"Conflitto: l'appuntamento delle {ora} del {data} si sovrappone "
                        "a uno già esistente."
                    )

        new_id = max((a.id for a in apps), default=0) + 1
        a = cls(new_id, patient_id, physio_id, data, ora, trattamento)
        apps.append(a)
        cls.save_all(apps)
        return a

    @classmethod
    def get_appointments(cls, physio_id=None, data=None, patient_id=None, id=None):
        apps = cls.load_all()
        results = []
        for a in apps:
            if physio_id is not None and a.physio_id != physio_id:
                continue
            if patient_id is not None and a.patient_id != patient_id:
                continue
            if data is not None and a.data != data:
                continue
            if id is not None and a.id != id:
                continue
            results.append(a)
        return sorted(results, key=lambda x: x.ora)

    @classmethod
    def cancel_appointment(cls, app_id):
        apps = cls.load_all()
        for a in apps:
            if a.id == app_id:
                a.stato = 'annullato'
                break
        cls.save_all(apps)

    @classmethod
    def record_session(cls, app_id, note=''):
        apps = cls.load_all()
        for a in apps:
            if a.id == app_id:
                a.stato = 'completato'
                a.note_cliniche = note
                break
        cls.save_all(apps)

    @classmethod
    def mark_reminder_sent(cls, app_id):
        apps = cls.load_all()
        for a in apps:
            if a.id == app_id:
                a.promemoria_inviato = True
                break
        cls.save_all(apps)
        return True
