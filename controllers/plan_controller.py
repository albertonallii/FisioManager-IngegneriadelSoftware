from models.plan import TreatmentPlan

def get_all_plans():
    return TreatmentPlan.load_all()

def create_treatment_plan(patient_id, descrizione):
    plans = TreatmentPlan.load_all()
    new_id = max([p.id for p in plans], default=0) + 1
    plan = TreatmentPlan(new_id, patient_id, descrizione, completato=False)
    plans.append(plan)
    TreatmentPlan.save_all(plans)
    return plan

def complete_treatment_plan(plan_id):
    plans = TreatmentPlan.load_all()
    changed = False
    for p in plans:
        if p.id == plan_id:
            setattr(p, "completato", True)
            changed = True
            break
    if changed:
        TreatmentPlan.save_all(plans)
    return changed

def update_treatment_plan(plan_id, patient_id, descrizione):
    plans = TreatmentPlan.load_all()
    changed = False
    for p in plans:
        if p.id == plan_id:
            setattr(p, "patient_id", patient_id)
            setattr(p, "descrizione", descrizione)
            changed = True
            break
    if changed:
        TreatmentPlan.save_all(plans)
    return changed

def delete_treatment_plan(plan_id):
    plans = TreatmentPlan.load_all()
    new_list = [p for p in plans if p.id != plan_id]
    if len(new_list) == len(plans):
        return False
    TreatmentPlan.save_all(new_list)
    return True
