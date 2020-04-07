from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.id = id
        self.name = name