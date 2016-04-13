import threading
import time
from email import encoders

from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify

from flask.ext.login import login_user, logout_user, login_required

from verifier_app.extensions import cache
from verifier_app.forms import LoginForm
from verifier_app.models import User, EmailEntry, db, DBStoredValue
from verifier_app.filters import *
from verifier_app.db_worker import Processor

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText

main = Blueprint('main', __name__)
thread = None


@main.route('/')
@cache.cached(timeout=1000)
@login_required
def home():
    return render_template('index.html')


@main.route('/check', methods=["GET", "POST"])
@login_required
def check():
    if request.method == 'POST':
        # Setting initial options to pass to 'result.html' template
        options = {}

        # Getting file with addresses
        uploaded_file = request.files['inputAddressFile']

        # And reading its content
        file_data = uploaded_file.read()
        # If there's content
        if file_data:
            # Then fill list with addresses
            address_list = file_data.split('\n')
            # And strip whitespaces
            address_list = [x.strip().lower() for x in address_list if "@" in x]

            # Saving initial length
            options["initial_len"] = len(address_list)
            store_value_in_db("initial_len", len(address_list))

            # Removing duplicates
            address_list = set(address_list)

            # And saving length without duplicates
            options["nodups_len"] = len(address_list)
            store_value_in_db("nodups_len", len(address_list))
        else:
            # Otherwise show an alert
            flash("Address list is empty", "danger")
            # And return
            return render_template('index.html')

        # Getting keywords file
        uploaded_file = request.files['inputKeywordFile']
        file_data = uploaded_file.read()
        keyword_list = []
        # Reading its data
        if file_data:
            keyword_list = file_data.split('\n')
            keyword_list = [word.strip().lower() for word in keyword_list]
        # If no data was transmitted, flash info alert
        else:
            flash("You didn't specify keywords list", "info")
        store_value_in_db("keyword_list_len", len(keyword_list))

        # The same with domains file
        uploaded_file = request.files['inputDomainFile']
        file_data = uploaded_file.read()
        domain_list = []
        if file_data:
            domain_list = file_data.split('\n')
            domain_list = [word.strip().lower() for word in domain_list]
        else:
            flash("You didn't specify domains list", "info")
        store_value_in_db("domain_list_len", len(domain_list))

        # And the same with MX records file
        uploaded_file = request.files['inputMXFile']
        file_data = uploaded_file.read()
        mx_list = []
        if file_data:
            mx_list = file_data.split('\n')
            mx_list = [word.strip().lower() for word in mx_list]
        else:
            flash("You didn't specify MX records list", "info")
        store_value_in_db("mx_list_len", len(mx_list))

        # At last, TOR usage
        use_tor = bool(request.form.getlist('useTOR'))
        if use_tor:
            pass
        else:
            flash("You don't use TOR network", "info")
        store_value_in_db("use_tor", use_tor)

        # And its rotation
        try:
            exit_node_rotation = int(request.form.getlist('exitNodeRotationNum')[0])
        except IndexError:
            exit_node_rotation = 0
        store_value_in_db("exit_node_rotation", exit_node_rotation)

        address_list = check_syntax(address_list)
        options["after_syntax_len"] = len(address_list)
        store_value_in_db("after_syntax_len", len(address_list))

        address_list = filter_keywords(address_list, keyword_list)
        options["after_keywords_len"] = len(address_list)
        store_value_in_db("after_keywords_len", len(address_list))

        address_list = filter_domains(address_list, domain_list)
        options["after_domains_len"] = len(address_list)
        store_value_in_db("after_domains_len", len(address_list))

        # Deleting previous data
        EmailEntry.query.delete()
        db.session.commit()

        for address in address_list:
            new_entry = EmailEntry(address)
            new_entry.set_processed(False)
            new_entry.set_validity(False)
            db.session.add(new_entry)

        while True:
            try:
                db.session.commit()
                break
            except Exception as e:
                print "During DB commit: " + str(e)
                time.sleep(1)

        p = Processor(mx_list, use_tor, exit_node_rotation)
        t = threading.Thread(target=p.start_processing)
        t.setDaemon(True)
        t.start()

        return redirect("/result")


def store_value_in_db(name, val):
    new_row = DBStoredValue(name, val)
    db.session.merge(new_row)
    db.session.commit()


def get_value_from_db(name):
    return db.session. \
        query(DBStoredValue). \
        filter_by(name=name). \
        first(). \
        get_value()


@main.route("/result")
@login_required
def show_result_page():
    options = {}

    return render_template("result.html", **options)


@main.route("/status")
@login_required
def get_tool_status():
    while True:
        try:
            result = {}
            total_count = EmailEntry.query.count()
            processed_count = EmailEntry.query.filter_by(processed=True).count()
            valid_count = EmailEntry.query.filter_by(validity=True).count()

            result["total_count"] = str(total_count)
            result["processed_count"] = str(processed_count)
            result["valid_count"] = str(valid_count)
            result["active_threads"] = threading.active_count() - 2

            result['progress_overall'] = (float(processed_count) / total_count) * 100
            result['progress_valid'] = (float(valid_count) / total_count) * 100

            result["initial_len"] = int(get_value_from_db("initial_len"))
            result["nodups_len"] = int(get_value_from_db("nodups_len"))
            result["after_syntax_len"] = int(get_value_from_db("after_syntax_len"))
            result["after_keywords_len"] = int(get_value_from_db("after_keywords_len"))
            result["after_domains_len"] = int(get_value_from_db("after_domains_len"))
            result["keyword_list_len"] = int(get_value_from_db("keyword_list_len"))
            result["domain_list_len"] = int(get_value_from_db("domain_list_len"))
            result["mx_list_len"] = int(get_value_from_db("mx_list_len"))
            result["use_tor"] = bool(get_value_from_db("use_tor"))
            result["exit_node_rotation"] = int(get_value_from_db("exit_node_rotation"))

            return jsonify(result)
        except Exception as e:
            print "During status fetch: " + str(e)


@main.route("/mail_results", methods=["POST"])
@login_required
def mail_results():
    # Mails .txt result to predefined address
    status = dict()

    status["valid_entry_len"] = EmailEntry.query.filter_by(validity=True).count()
    status["spam_entry_len"] = EmailEntry.query.filter_by(spam=True).count()

    with open("result.txt", "wb") as f:
        for valid_entry in EmailEntry.query.filter_by(validity=True):
            f.write("{0}\r\n".format(valid_entry.get_address()))

    with open("spam.txt", "wb") as f:
        for valid_entry in EmailEntry.query.filter_by(spam=True):
            f.write("{0}\r\n".format(valid_entry.get_address()))

    # "From" address built upon AWS instance's public DNS
    from_address = "bot@localhost"
    to_address = request.form["address"]
    status["address"] = to_address

    # Preparing message
    msg = MIMEMultipart()

    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = "Email addresses verification result"

    body = "Check attachment."

    msg.attach(MIMEText(body, 'plain'))

    # And first attachment
    attachment = open("result.txt", "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename=result.txt")

    msg.attach(part)

    # And spam attachment
    attachment = open("spam.txt", "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename=spam.txt")

    msg.attach(part)

    try:
        # And sending it
        from smtplib import SMTP
        server = SMTP('localhost')
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()

        status["success"] = True

    except Exception as e:
        status["success"] = False
        print e

    return jsonify(status)


@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user)

        flash("Logged in successfully.", "success")
        return redirect(request.args.get("next") or url_for(".home"))

    return render_template("login.html", form=form)


@main.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")

    return redirect(url_for(".home"))
