from models.user import User
import bcrypt

def _is_admin(user) -> bool:
    return str(getattr(user, "ruolo", "")).strip().lower() in ("amministratore", "admin")

def _normalize_role(ruolo: str) -> str:
    return "amministratore" if str(ruolo).strip().lower() in ("admin", "amministratore") \
           else "fisioterapista"

def get_all_users():
    return User.load_all()

def create_new_user(nome, email, password, ruolo):
    role = _normalize_role(ruolo)
    return User.create_user(nome, email, password, role)

def update_user(user_id, nome=None, email=None, password=None, ruolo=None):
    users = User.load_all()
    u = next((x for x in users if x.id == user_id), None)
    if not u:
        return False

    if email and email != u.email:
        if any(x.email == email for x in users):
            return False

    new_role = _normalize_role(ruolo) if ruolo is not None else u.ruolo
    if _is_admin(u) and new_role not in ("amministratore", "admin"):
        admins = [x for x in users if _is_admin(x)]
        if len(admins) <= 1:
            return False
    if nome is not None:
        u.nome = nome
    if email is not None:
        u.email = email
    if password:
        u.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    if ruolo is not None:
        u.ruolo = new_role

    User.save_all(users)
    return True

def delete_user(user_id):
    users = User.load_all()
    target = next((x for x in users if x.id == user_id), None)
    if not target:
        return False

    if _is_admin(target):
        admins = [x for x in users if _is_admin(x)]
        if len(admins) <= 1:
            return False

    users = [x for x in users if x.id != user_id]
    User.save_all(users)
    return True
