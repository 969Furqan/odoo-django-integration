import xmlrpc.client
from invoices.odoo_client import _get_odoo_env


def fetch_odoo_invoices():
    env = _get_odoo_env()
    url = env["url"]
    db = env["db"]
    username = env["user"]
    password = env["password"]

    # XML-RPC endpoints
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise RuntimeError("Odoo authentication failed: Access Denied")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    data = models.execute_kw(
        db,
        uid,
        password,
        "account.move",
        "search_read",
        [[["move_type", "=", "out_invoice"]]],
        {"limit": 50},
    )

    # Convert to Django model format
    return [
        {
            "id": r["id"],
            "name": r.get("name", ""),
            "partner": (r.get("partner_id") or [None, ""])[1] if isinstance(r.get("partner_id"), list) else "",
            "invoice_date": r.get("invoice_date"),
            "amount_total": r.get("amount_total"),
            "data": r,
        }
        for r in data
    ]
