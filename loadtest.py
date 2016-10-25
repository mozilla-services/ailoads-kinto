import os
import uuid
import random

from ailoads.fmwk import scenario, requests

random = random.SystemRandom()


# Read configuration from env
SERVER_URL = os.getenv('KINTO_SERVER_URL',
                       "https://kinto.stage.mozaws.net:443").rstrip('/')

_CONNECTIONS = {}

_COLLECTIONS = [
    "/buckets/blocklists/collections/certificates/records",
    "/buckets/blocklists/collections/addons/records",
    "/buckets/blocklists/collections/plugins/records",
    "/buckets/blocklists/collections/gfx/records",
    "/buckets/monitor/collections/changes/records",
    "/buckets/fennec/collections/catalog/records",
    "/buckets/fennec/collections/experiments/records",
]

_BLOCKLISTS_URLS = [
    "/blocklist/3/{3550f703-e582-4d05-9a08-453d09bdfdc6}/47.0/",  # Thunderbird
    "/blocklist/3/{ec8030f7-c20a-464f-9b0e-13a3a9e97384}/47.0/",  # Firefox
]

_HEARTBEAT_URL = "/v1/__heartbeat__"

_STATUS_URL = "/v1/"


def get_random_string(length=50,
                      allowed_chars='/abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Returns a securely generated random string.
    The default length of 50 with the a-z, A-Z, 0-9 and / character set returns
    a 71-bit value. log_2((26+26+11)^50) =~ 643 bits
    """
    return ''.join(random.choice(allowed_chars) for i in range(length))


def get_connection(conn_id=None):
    if conn_id is None or conn_id not in _CONNECTIONS:
        conn = KintoConnection(uuid.uuid4().hex)
        _CONNECTIONS[conn_id] = conn

    return _CONNECTIONS[conn_id]


class KintoConnection(object):

    def __init__(self, id):
        self.id = id
        self.headers = {}
        self.timeout = 60  # 1 minute is a long time already

    def get(self, endpoint):
        return requests.get(
            SERVER_URL + endpoint,
            headers=self.headers,
            timeout=self.timeout)

    def post(self, endpoint, data):
        return requests.post(
            SERVER_URL + endpoint,
            json=data,
            headers=self.headers,
            timeout=self.timeout)

    def put(self, endpoint, data):
        return requests.put(
            SERVER_URL + endpoint,
            json=data,
            headers=self.headers,
            timeout=self.timeout)

    def delete(self, endpoint):
        return requests.delete(
            SERVER_URL + endpoint,
            headers=self.headers,
            timeout=self.timeout)


@scenario(30)
def access_bucket_collection_records():
    """Access the list of records."""
    conn = get_connection('system.Everyone')
    url = random.choice(_COLLECTIONS)

    r = conn.get(url)
    r.raise_for_status()
    body = r.json()
    assert "data" in body, "data not found in body"


@scenario(30)
def access_bucket_collection_metadata():
    """Access collection metadata"""
    conn = get_connection('system.Everyone')
    url = random.choice(_COLLECTIONS).replace('/records', '')

    r = conn.get(url)
    r.raise_for_status()
    body = r.json()
    assert "data" in body, "data not found in body"


@scenario(30)
def access_blocklist_url():
    """Access blocklist URLs"""
    conn = get_connection('system.Everyone')
    url = random.choice(_BLOCKLISTS_URLS)
    salted_url = '%s%s' % (url, get_random_string())
    r = conn.get(salted_url)
    r.raise_for_status()
    assert r.text.startswith('<?xml'), "Doesn't starts with an XML header."


@scenario(5)
def access_heartbeat_url():
    """ Access heartbeat URL"""
    conn = get_connection('system.Everyone')
    url = _HEARTBEAT_URL
    r = conn.get(url)
    r.raise_for_status()
    body = r.json()
    assert "attachments" in body
    assert "cache" in body
    assert "permission" in body
    assert "storage" in body


@scenario(5)
def access_status_url():
    """ Access status URL """
    conn = get_connection('system.Everyone')
    url = _STATUS_URL
    r = conn.get(url)
    r.raise_for_status()
    body = r.json()
    assert "url" in body
    assert "project_name" in body
