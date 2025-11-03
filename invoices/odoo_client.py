import logging
import requests
import xmlrpc.client
from django.conf import settings

logger = logging.getLogger(__name__)



def _get_odoo_env() -> dict:
    return {
        'url': settings.ODOO_URL,
        'db': settings.ODOO_DB,  # <--- IMPORTANT: Database name = subdomain
        'user': settings.ODOO_USERNAME,  # The login email you use to sign in
        'password': settings.ODOO_PASSWORD,  # Your API key
    }


def _json_rpc(url, method, params):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    result = response.json()
    if 'error' in result:
        raise RuntimeError(result['error'])
    return result['result']


def fetch_invoice_field_names():
    """Fetch field names from Odoo using XML-RPC."""
    env = _get_odoo_env()
    url = env['url']
    db = env['db']
    username = env['user']
    password = env['password']

    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise RuntimeError("Odoo authentication failed")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    fields = models.execute_kw(
        db,
        uid,
        password,
        "account.move",
        "fields_get",
        [],
        {"attributes": ["string", "type", "required"]},
    )

    return sorted(fields.keys())


def try_log_invoice_fields_on_startup():
    """Best-effort logging at Django startup."""
    try:
        names = fetch_invoice_field_names()
        logger.info("Odoo invoice (account.move) fields (%d): %s", len(names), ", ".join(names))
    except Exception as exc:
        logger.warning("Could not fetch Odoo invoice fields at startup: %s", exc)
