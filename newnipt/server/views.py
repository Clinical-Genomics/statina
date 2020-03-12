#!/usr/bin/env python

from flask import url_for, redirect, render_template, request, Blueprint, current_app

app = current_app
blueprint = Blueprint('server', __name__ )

@blueprint.route('/', methods=['GET', 'POST'])
def index():
    return render_template(
        'index.html')
