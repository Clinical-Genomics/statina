from flask import url_for
from flask_login import current_user
from flask_ldap3_login.forms import LDAPLoginForm
from newnipt.server import create_app


app = create_app(test= True)
app.register_blueprint(login_bp)
app.register_blueprint(server_bp)
login_manager.init_app(app)
from newnipt.server.login import login_bp, login_manager
from newnipt.server.views import server_bp

def test_authorized_login():
    """Test successful authentication against scout database"""

    # GIVEN an initialized app
    # WHEN trying to access scout with the email of an existing user



    with app.test_client() as client:
        resp = client.get(url_for("login.login"))
        print(dir(resp))
        # THEN response should redirect to user institutes
        assert resp.status_code == 302
        # And current user should be authenticated
        assert current_user.is_authenticated