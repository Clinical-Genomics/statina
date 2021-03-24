

def load_user(adapter, email: str, name: str, role: str)-> None:
    """Function to load a new user to the database."""
    
    user = {'_id': email, 'email': email, 'name': name, 'role': role}
    adapter.add_or_update_document(user, adapter.user_collection)
