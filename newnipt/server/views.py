#!/usr/bin/env python

from flask import (
    url_for,
    redirect,
    render_template,
    request,
    Blueprint,
    current_app,
    session,
    flash,
)
from flask_login import login_required
from datetime import datetime
from newnipt.server.utils import *
from newnipt.server.constants import *
app = current_app
server_bp = Blueprint("server", __name__)


@server_bp.route("/", methods=["GET", "POST"])
def index():
    user = session.get("user")
    if user:
        return redirect(url_for("server.batches"))
    return render_template("index.html", user=user)


@server_bp.route("/batches")
@login_required
def batches():
    all_batches = list(app.adapter.batches())
    return render_template("batches.html", batches=all_batches)


@server_bp.route("/batches/<batch_id>/")
@login_required
def batch(batch_id):
    samples = app.adapter.batch_samples(batch_id)
    batch = app.adapter.batch(batch_id)

    return render_template("batch/batch.html",
        batch = batch,
        sample_info = [get_sample_info(sample) for sample in samples],
        #warnings = ...,
        sample_ids = ",".join(sample.get("_id") for sample in samples),
        page_id = "batches",
    )


@server_bp.route("/samples/<sample_id>/")
@login_required
def sample(sample_id):
    sample = app.adapter.sample(sample_id)
    batch = app.adapter.batch(sample.get('Flowcell'))

    return render_template("sample/sample.html",
        chrom_abnorm = CHROM_ABNORM,
        sample = sample,
        status_classes = STATUS_CLASSES,
        batch = batch)

@server_bp.route("/samples/<sample_id>/tris")
@login_required
def sample_tris(sample_id):
    sample = app.adapter.sample(sample_id)
    batch = app.adapter.batch(sample.get('Flowcell'))

    return render_template("sample/sample_tris.html",
        tris_abn_status = get_tris_abn_for_plot(app.adapter),
        sample = sample,
        batch = batch,
        status_colors = STATUS_COLORS,
        page_id="sample_tris",
    )


@server_bp.route('/NIPT/<batch_id>/<sample_id>/update_trisomi_status', methods=['POST'])
@login_required
def update_trisomi_status(batch_id, sample_id):
    time_stamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    sample = app.adapter.sample(sample_id)
    user = app.user
    for abnormality in CHROM_ABNORM:
        new_abnormality_status = request.form[abnormality]
        if sample.get(f"status_{abnormality}") != new_abnormality_status:
            sample[f"status_{abnormality}"] = new_abnormality_status
            sample[f"status_change_{abnormality}"] = ' '.join([user.name, time_stamp])

    if user.role == 'RW':
        app.adapter.add_or_update_document(sample, app.adapter.sample_collection)
        return redirect(request.referrer)
    else:
        return '', 201

@server_bp.route("/update", methods=["POST"])
@login_required
def update():
    return redirect(request.referrer)


@server_bp.route("/batches/<batch_id>/NCV13")
@login_required
def NCV13(batch_id):
    batch = app.adapter.batch(batch_id)

    return render_template(
        "batch/NCV13.html",
        batch=batch,
        page_id="batches_NCV13",
    )


@server_bp.route("/batches/<batch_id>/NCV18")
@login_required
def NCV18(batch_id):
    batch = app.adapter.batch(batch_id)
    return render_template(
        "batch/NCV18.html",
        batch=batch,
        page_id="batches_NCV18",
    )


@server_bp.route("/batches/<batch_id>/NCV21")
@login_required
def NCV21(batch_id):
    batch = app.adapter.batch(batch_id)
    return render_template(
        "batch/NCV21.html",
        batch=batch,
        page_id="batches_NCV21",
    )


@server_bp.route("/batches/<batch_id>/fetal_fraction")
@login_required
def fetal_fraction(batch_id):
    batch = app.adapter.batch(batch_id)
    return render_template(
        "batch/fetal_fraction.html",
        batch=batch,
        page_id="batches_FF",
    )


@server_bp.route("/batches/<batch_id>/covX_covY")
@login_required
def covX_covY(batch_id):
    batch = app.adapter.batch(batch_id)
    return render_template(
        "batch/covX_covY.html",
        batch=batch,
        page_id="batches_cov_xy",
    )


@server_bp.route("/batches/<batch_id>/coverage")
@login_required
def coverage(batch_id):
    batch = app.adapter.batch(batch_id)
    return render_template(
        "batch/coverage.html",
        batch=batch,
        page_id="batches_cov",
    )


@server_bp.route("/batches/<batch_id>/report/<coverage>")
@login_required
def report(batch_id, coverage):
    return render_template("batch/report.html", batch_id=batch_id)
