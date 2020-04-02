#!/usr/bin/env python

from flask import url_for, redirect, render_template, request, Blueprint, current_app, session
from authlib.integrations.flask_client import OAuth

app = current_app
blueprint = Blueprint('server', __name__ )


CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    } 
    )     
       

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
    
    
@blueprint.route('/authorized')
def authorized(): 
    token = oauth.google.authorize_access_token()
    print(token)
    user = oauth.google.parse_id_token(token)
    print(user)
    session['user'] = user
    return redirect('/')


@blueprint.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')