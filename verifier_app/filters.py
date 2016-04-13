import re
import socket
import smtplib
from random import randint, choice

import dns.resolver
import socks
from dns.resolver import NXDOMAIN
from stem import Signal
from stem.control import Controller

TOR_HOST = '127.0.0.1'
TOR_PORT = [9051, 9052, 9053, 9054, 9055]


def filter_keywords(address_list, keyword_list):
    result = []

    for address in address_list:
        if any(keyword in address for keyword in keyword_list):
            continue
        else:
            result.append(address)

    return result


def filter_domains(address_list, domain_list):
    result = []

    for address in address_list:
        if any(domain in address for domain in domain_list):
            continue
        else:
            result.append(address)

    return result


def check_syntax(address_list):
    result = []

    # Simple Regex for syntax checking
    regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'

    # Email address to verify
    for address in address_list:
        # Syntax check
        if re.match(regex, address):
            result.append(address)

    return result