#!/usr/bin/env python

from flask import url_for, redirect, render_template, request, Blueprint, current_app, session, flash
from flask_login import  login_required

app = current_app
server_bp = Blueprint('server', __name__ )


@server_bp.route('/', methods=['GET', 'POST'])
def index():
    user = session.get('user')
    if user:
        return redirect(url_for('server.batch'))
    return render_template(
        'index.html',
        user=user)


@server_bp.route('/NIPT')
@login_required
def batch():
    return render_template('start_page.html')