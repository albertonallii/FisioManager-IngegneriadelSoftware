from models import storage

class TreatmentPlan:
    file_name = 'plans.json'

    def __init__(self, id, patient_id, descrizione, completato=False):
        self.id = id
        self.patient_id = patient_id
        self.descrizione = descrizione
        self.completato = completato

    def to_dict(self):
        return self.__dict__

    @classmethod
    def load_all(cls):
        return [cls(**item) for item in storage.load_data(cls.file_name)]

    @classmethod
    def save_all(cls, plans):
        storage.save_data(cls.file_name, [p.to_dict() for p in plans])

    @classmethod
    def create_plan(cls, patient_id, descrizione):
        plans = cls.load_all()
        new_id = max([p.id for p in plans], default=0) + 1
        plan = cls(new_id, patient_id, descrizione)
        plans.append(plan)
        cls.save_all(plans)
        return plan

    @classmethod
    def mark_completed(cls, plan_id):
        plans = cls.load_all()
        for p in plans:
            if p.id == plan_id:
                p.completato = True
                break
        cls.save_all(plans)

    @classmethod
    def get_plans_by_patient(cls, pid):
        return [p for p in cls.load_all() if p.patient_id == pid]
