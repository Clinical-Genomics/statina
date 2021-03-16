from NIPTool.schemas.server.load import UserLoadModel
from NIPTool.load.user import load_user
from NIPTool.adapter.plugin import NiptAdapter


def test_load_user(database):
    # GIVEN a user with valid requiered fields and a nipt database adapter
    user = UserLoadModel(email='maya.papaya@something.se', name="Maya Papaya", role="RW")
    nipt_adapter = NiptAdapter(database.client, db_name='test')

    # WHEN running load_user
    load_user(nipt_adapter, user)

    # The user should be added to the database
    assert nipt_adapter.user_collection.estimated_document_count() == 1
