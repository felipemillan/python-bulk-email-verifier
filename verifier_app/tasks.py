import os
import smtplib
import socket
from random import choice
from random import randint

import dns
import socks
from dns.resolver import NXDOMAIN, NoAnswer
from stem import Signal
from stem.control import Controller
from sqlite3 import OperationalError
from datab import db_session as session
from extensions import celery_client

TOR_HOST = '127.0.0.1'
TOR_PORT = [9051, 9052, 9053, 9054]

import celery
import multiprocessing


class WorkerProcess(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        argv = [
            'worker',
            '--loglevel=INFO',
            '--concurrency=24',
        ]
        celery_client.worker_main(argv)
        celery_client.control.time_limit('verifier_app.tasks.verify_address', soft=45, hard=60, reply=True)


def start_celery():
    os.environ["C_FORCE_ROOT"] = 'true'
    global worker_process
    worker_process = WorkerProcess()
    worker_process.start()


def stop_celery():
    celery_client.control.purge()
    global worker_process
    if worker_process:
        worker_process.terminate()
        worker_process = None


def clear_all_tasks():
    celery_client.control.purge()


worker_name = 'celery@local'
worker_process = None


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # session.remove()
        pass


# Custom connection for SMTP lib
def tor_custom_connect(host, port, timeout):
    sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setproxy(socks.PROXY_TYPE_SOCKS5, TOR_HOST, choice(TOR_PORT))
    sock.connect((host, port))
    print str((TOR_HOST, TOR_PORT)) + 'connect:' + str((host, port))
    if isinstance(timeout, int) or isinstance(timeout, str) or isinstance(timeout, float):
        sock.settimeout(float(timeout))
    return sock


def change_tor_node(port):
    with Controller.from_port(port=port) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        print "!!! Changed TOR node"

@celery_client.task(base=SqlAlchemyTask, max_retries=3, default_retry_delay=10, name='tasks.verify_address')
def verify_address(entry, mx_list, use_tor, rotation_num):
    address = entry.get_address()

    spam = False
    a_record = True
    code, message = None, None

    # Address used for SMTP MAIL FROM command
    from_address = "checker@someplace.com"

    # Email address to verify
    address_to_verify = str(address)

    # Get domain for DNS lookup
    split_address = address_to_verify.split('@')
    domain = str(split_address[1])

    # Check for 'A' record
    try:
        records = dns.resolver.query(domain, 'A')
    except NXDOMAIN:
        a_record = False
    except NoAnswer:
        a_record = False

    # MX record lookup
    records = dns.resolver.query(domain, 'MX')
    address_mx_record = records[0].exchange
    address_mx_record = str(address_mx_record)

    # Checking MX records from list. If any found, then return false
    if any(mx_record in address_mx_record for mx_record in mx_list):
        validity = False
        if "spam" in address_mx_record:
            spam = True
        else:
            spam = False
        return validity, spam

    # Get local server hostname
    host = socket.gethostname()

    server = smtplib.SMTP()
    server.set_debuglevel(0)

    # SMTP lib setup (use debug level for full output)
    if use_tor:
        server._get_socket = tor_custom_connect

    if use_tor and rotation_num:
        if rotation_num == randint(0, rotation_num):
            for tor_port in TOR_PORT:
                # change_tor_node(tor_port)
                pass

    # SMTP Conversation
    try:
        server.connect(address_mx_record)
        server.helo(host)
        server.mail(from_address)
        code, message = server.rcpt(str(address_to_verify))
        server.quit()
    except Exception as e:
        print e
        validity = False

    # Assume SMTP response 250 is success
    if code == 250 and a_record:
        validity = True
    else:
        validity = False

    # finally:
    entry.set_validity(validity)
    entry.set_spam(spam)
    entry.set_processed(True)

    session.add(entry)
    try:
        session.flush()
    except Exception:
        return None
