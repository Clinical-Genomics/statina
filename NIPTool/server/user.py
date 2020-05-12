from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, name, id, role, active=True):
        self.id = id
        self.role = role
        self.name = name