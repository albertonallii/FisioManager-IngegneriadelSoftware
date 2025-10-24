from models.user import User

def attempt_login(email, password):
    return User.authenticate(email, password)

def recover_password(email):
    return User.get_by_email(email) is not None
