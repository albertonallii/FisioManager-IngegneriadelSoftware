from models.appointment import Appointment

def create_new_appointment(patient_id, physio_id, data, ora, trattamento=''):
    try:
        return Appointment.create_appointment(patient_id, physio_id, data, ora, trattamento)
    except ValueError:
        return None

def get_schedule_for_date(user, data=None):
    if user.ruolo == 'amministratore':
        return Appointment.get_appointments(data=data)
    return Appointment.get_appointments(physio_id=user.id, data=data)

def cancel_appointment(app_id):
    Appointment.cancel_appointment(app_id)

def complete_appointment(app_id, note=''):
    Appointment.record_session(app_id, note)

def send_appointment_reminder(app_id):
    return Appointment.mark_reminder_sent(app_id)
