#!/usr/bin/env python

from flask import url_for, redirect, request, Blueprint, session, current_app
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

from newnipt.server.user import User

app = current_app
login_manager = LoginManager()
login_bp = Blueprint('login', __name__ )
oauth = OAuth(app)

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'} 
    )

@login_bp.route('/login')
def login():
    redirect_uri = url_for('login.authorized', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@login_bp.route('/logout')
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


@login_bp.route('/authorized')
def authorized(): 
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    authorized_user = app.adapter.user(user.email)
    if authorized_user is None:
        flash('Your email is not on the whitelist, contact an admin.')
        return redirect(url_for('server.index'))
    session['user'] = user
    return redirect(url_for('server.batch'))
