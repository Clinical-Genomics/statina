#!/usr/bin/env python

from flask import url_for, redirect, render_template, request, Blueprint, current_app, session, flash
from flask_login import  login_required, LoginManager, UserMixin
from authlib.integrations.flask_client import OAuth

app = current_app
login_manager = LoginManager()
blueprint = Blueprint('server', __name__ )


oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'} 
    )     

class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.id = id
       

@blueprint.route('/', methods=['GET', 'POST'])
def index():
    user = session.get('user')
    return render_template(
        'index.html',
        user=user)


@blueprint.route('/login')
def login():
    redirect_uri = url_for('server.authorized', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@blueprint.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@login_manager.request_loader
def request_loader(request):
    if not session.get('user'):
        return
    email = session['user'].get('email')
    name = session['user'].get('name')
    if not app.adapter.user(email):
        return

    user = User(name, email)
    return user


@blueprint.route('/authorized')
def authorized(): 
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    authorized_user = app.adapter.user(user.email)
    if authorized_user is None:
        flash('Your email is not on the whitelist, contact an admin.')
        return redirect(url_for('server.index'))
    session['user'] = user
    return redirect(url_for('server.batch'))


@blueprint.route('/NIPT')
@login_required
def batch():
    return render_template('start_page.html')