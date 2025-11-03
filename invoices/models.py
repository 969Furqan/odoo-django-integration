from django.db import models

class OdooInvoice(models.Model):
    """A virtual model representing an Odoo invoice — no database table."""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    partner = models.CharField(max_length=255, blank=True, null=True)
    invoice_date = models.CharField(max_length=50, blank=True, null=True)
    amount_total = models.FloatField(blank=True, null=True)
    data = models.JSONField(blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = "Odoo Invoice"
        verbose_name_plural = "Odoo Invoices"

    def __str__(self):
        return self.name
