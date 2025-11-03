from django.apps import AppConfig


class InvoicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invoices'
    verbose_name = 'Invoices'

    def ready(self):
        # Attempt to log invoice field names at startup if env vars are present
        from .odoo_client import try_log_invoice_fields_on_startup
        try_log_invoice_fields_on_startup()
