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


### Sample views


@server_bp.route("/samples/<sample_id>/")
@login_required
def sample(sample_id):
    sample = app.adapter.sample(sample_id)
    batch = app.adapter.batch(sample.get('SampleProject'))

    return render_template("sample/sample.html",
        chrom_abnorm = CHROM_ABNORM,
        sample = sample,
        status_classes = STATUS_CLASSES,
        batch = batch)

@server_bp.route("/samples/<sample_id>/tris")
@login_required
def sample_tris(sample_id):
    sample = app.adapter.sample(sample_id)
    batch = app.adapter.batch(sample.get('SampleProject'))
    abnormal_data, data_per_abnormaliy = get_abn_for_samp_tris_plot(app.adapter)
    normal_data = get_normal_for_samp_tris_plot(app.adapter)
    sample_data = get_sample_for_samp_tris_plot(sample)
    return render_template("sample/sample_tris.html",
        tris_abn = data_per_abnormaliy,
        normal_data = normal_data,
        abnormal_data = abnormal_data, 
        sample_data = sample_data,
        sample = sample,
        batch = batch,
        status_colors = STATUS_COLORS,
        page_id="sample_tris",
    )

@server_bp.route("/batches/<batch_id>/")
@login_required
def batch(batch_id):

    samples = app.adapter.batch_samples(batch_id)
    batch = app.adapter.batch(batch_id)
    return render_template("batch/batch.html",
        batch = batch,
        sample_info = [get_sample_info(sample) for sample in samples],
        #warnings = ...,
        #sample_ids = ",".join(sample.get("_id") for sample in samples),
        page_id = "batches",
    )


@server_bp.route("/batches/<batch_id>/NCV13")
@login_required
def NCV13(batch_id):
    return render_template(
        "batch/NCV.html",
        batch = app.adapter.batch(batch_id),
        chrom = '13',
        cases = get_case_data_for_batch_tris_plot(app.adapter, '13', batch_id),
        normal_data = get_normal(app.adapter, '13'),
        abnormal_data = get_abnormal(app.adapter, '13', 0),
        page_id = "batches_NCV13"
    )

@server_bp.route("/batches/<batch_id>/NCV18")
@login_required
def NCV18(batch_id):
    return render_template(
        "batch/NCV.html",
        batch = app.adapter.batch(batch_id),
        chrom = '18',
        cases = get_case_data_for_batch_tris_plot(app.adapter, '18', batch_id),
        normal_data = get_normal(app.adapter, '18'),
        abnormal_data = get_abnormal(app.adapter, '18', 0),
        page_id = "batches_NCV18"
    )

@server_bp.route("/batches/<batch_id>/NCV21")
@login_required
def NCV21(batch_id):
    return render_template(
        "batch/NCV.html",
        batch = app.adapter.batch(batch_id),
        chrom = '21',
        cases = get_case_data_for_batch_tris_plot(app.adapter, '21', batch_id),
        normal_data = get_normal(app.adapter, '21'),
        abnormal_data = get_abnormal(app.adapter, '21', 0),
        page_id = "batches_NCV21"
    )

@server_bp.route("/batches/<batch_id>/fetal_fraction_XY")
@login_required
def fetal_fraction_XY(batch_id):
    batch = app.adapter.batch(batch_id)
    control = get_ff_control(app.adapter)
    abnormal = get_ff_abnormal(app.adapter)
    return render_template(
        "batch/fetal_fraction_XY.html",
        control = control,
        abnormal = abnormal,
        cases = get_ff_cases(app.adapter, batch_id),
        max_x = max(control['FFX']) +1,
        min_x = min(control['FFX']) -1,
        batch=batch,
        page_id="batches_FF_XY",
    )

@server_bp.route("/batches/<batch_id>/fetal_fraction")
@login_required
def fetal_fraction(batch_id):
    batch = app.adapter.batch(batch_id)
    return render_template(
        "batch/fetal_fraction.html",
        control = get_ff_control(app.adapter),
        cases = get_ff_cases(app.adapter, batch_id),
        batch=batch,
        page_id="batches_FF",
    )


@server_bp.route("/batches/<batch_id>/coverage")
@login_required
def coverage(batch_id):
    batch = app.adapter.batch(batch_id)
    samples = app.adapter.batch_samples(batch_id)
    data = get_data_for_coverage_plot(samples)
    return render_template(
        "batch/coverage.html",
        batch = batch,
        x_axis = list(range(1,23)),
        data = data,
        page_id = "batches_cov",
    )


@server_bp.route("/batches/<batch_id>/report/<coverage>")
@login_required
def report(batch_id, coverage):
    return render_template("batch/report.html", batch_id=batch_id)


@server_bp.route('/update', methods=['POST'])
@login_required
def update():
    time_stamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    user = app.user
    if user.role != 'RW':
        return '', 201

    if request.form.get('form_id') == 'set_sample_status':
        sample_id=request.form['sample_id']
        sample = app.adapter.sample(sample_id)
        for abnormality in CHROM_ABNORM:
            new_abnormality_status = request.form[abnormality]
            if sample.get(f"status_{abnormality}") != new_abnormality_status:
                sample[f"status_{abnormality}"] = new_abnormality_status
                sample[f"status_change_{abnormality}"] = ' '.join([user.name, time_stamp])
        app.adapter.add_or_update_document(sample, app.adapter.sample_collection)
            
    if request.form.get('form_id') == 'set_sample_comment':
        sample_id=request.form['sample_id']
        sample = app.adapter.sample(sample_id)
        if request.form.get('comment') != sample.get('comment'):
            sample['comment'] = request.form.get('comment')
        app.adapter.add_or_update_document(sample, app.adapter.sample_collection)
    
    if request.form.get('button_id') == 'Save':
        samples = request.form.getlist('samples')
        for sample_id in samples:
            sample = app.adapter.sample(sample_id)
            comment = request.form.get(f"comment_{sample_id}")
            include = request.form.get(f"include_{sample_id}")
            if comment != sample.get('comment'):
                sample['comment'] = comment
            if include and sample.get('include', False) == False:
                sample['include'] = True
                sample['change_include_date'] = ' '.join([user.name, time_stamp])
            elif not include and sample.get('include') == True:
                sample['include'] = False
            app.adapter.add_or_update_document(sample, app.adapter.sample_collection)
    
    if request.form.get('button_id') =='include all samples':
        samples = request.form.getlist('samples')
        for sample_id in samples:
            sample = app.adapter.sample(sample_id)
            if sample.get('include', False) == False:
                sample['include'] = True
                sample['change_include_date'] = ' '.join([user.name, time_stamp])
                app.adapter.add_or_update_document(sample, app.adapter.sample_collection)

    return redirect(request.referrer)

