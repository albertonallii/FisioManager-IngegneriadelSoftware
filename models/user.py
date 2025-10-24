from models import storage
import bcrypt

class User:
    file_name = 'users.json'

    def __init__(self, id, nome, email, password, ruolo):
        self.id = id
        self.nome = nome
        self.email = email
        self.password = password
        self.ruolo = ruolo

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "password": self.password,
            "ruolo": self.ruolo
        }

    @classmethod
    def load_all(cls):
        data = storage.load_data(cls.file_name)
        return [cls(item["id"], item["nome"], item["email"], item["password"], item["ruolo"]) for item in data]

    @classmethod
    def save_all(cls, users):
        storage.save_data(cls.file_name, [u.to_dict() for u in users])

    @classmethod
    def get_by_email(cls, email):
        for u in storage.load_data(cls.file_name):
            if u["email"] == email:
                return cls(u["id"], u["nome"], u["email"], u["password"], u["ruolo"])
        return None

    @classmethod
    def authenticate(cls, email, password):
        user = cls.get_by_email(email)
        if user and bcrypt.checkpw(password.encode(), user.password.encode()):
            return user
        return None

    @classmethod
    def create_user(cls, nome, email, password, ruolo):
        users = cls.load_all()
        if any(u.email == email for u in users):
            return None
        new_id = max([u.id for u in users], default=0) + 1
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        new_user = cls(new_id, nome, email, hashed, ruolo)
        users.append(new_user)
        cls.save_all(users)
        return new_user
