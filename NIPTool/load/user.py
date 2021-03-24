
from NIPTool.schemas.server.load import UserLoadModel
from NIPTool.adapter.plugin import NiptAdapter

def load_user(adapter: NiptAdapter, user: UserLoadModel)-> None:
    """Function to load a new user to the database."""
    
    user = {'_id': user.email, 'email': user.email, 'name': user.name, 'role': user.role}
    adapter.add_or_update_document(user, adapter.user_collection)
