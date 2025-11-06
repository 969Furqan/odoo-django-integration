import json
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from .models import OdooInvoice
from .services.odoo_invoices import fetch_odoo_invoices

@admin.register(OdooInvoice)
class OdooInvoiceAdmin(admin.ModelAdmin):
    list_display = ("name", "partner", "invoice_date", "amount_total", "data_preview")
    search_fields = ("name", "partner")
    readonly_fields = ("pretty_data", "download_ubl_button")

    fieldsets = (
        (None, {
            "fields": ("name", "partner", "invoice_date", "amount_total")
        }),
        ("Raw Odoo Data", {
            "fields": ("pretty_data",),
        }),
        ("Actions", {
            "fields": ("download_ubl_button",),
        }),
    )

    def get_queryset(self, request):
        try:
            invoices = fetch_odoo_invoices()
        except Exception as exc:
            self.message_user(request, f"Odoo error: {exc}", level=messages.ERROR)
            return OdooInvoice.objects.none()

        # Sync fetched invoices into DB so admin can use a proper QuerySet
        ids = set()
        objs = []
        for inv in invoices:
            ids.add(inv["id"])
            objs.append(
                OdooInvoice(
                    id=inv["id"],
                    name=inv["name"],
                    partner=inv["partner"],
                    invoice_date=inv["invoice_date"],
                    amount_total=inv["amount_total"],
                    data=inv.get("data"),
                )
            )

        if objs:
            OdooInvoice.objects.bulk_create(
                objs,
                update_conflicts=True,
                update_fields=["name", "partner", "invoice_date", "amount_total", "data"],
                unique_fields=["id"],
            )

        # Remove stale rows not present in the current fetch
        if ids:
            OdooInvoice.objects.exclude(id__in=ids).delete()
        else:
            OdooInvoice.objects.all().delete()

        return OdooInvoice.objects.all()

    def data_preview(self, obj):
        if not obj.data:
            return ""
        try:
            json_str = json.dumps(obj.data, indent=2, ensure_ascii=False)
        except Exception:
            return str(obj.data)
        # Limit preview to avoid huge rows
        if len(json_str) > 500:
            json_str = json_str[:500] + "\n…"
        return format_html("<pre style=\"white-space:pre-wrap;max-width:600px;overflow:auto;margin:0\">{}</pre>", json_str)
    data_preview.short_description = "Data"

    def pretty_data(self, obj):
        if not obj.data:
            return ""
        try:
            json_str = json.dumps(obj.data, indent=2, ensure_ascii=False)
        except Exception:
            return str(obj.data)
        return format_html("<pre style=\"white-space:pre-wrap;max-height:70vh;overflow:auto\">{}</pre>", json_str)
    pretty_data.short_description = "Data (pretty JSON)"

    def download_ubl_button(self, obj):
        try:
            url = reverse("invoice_download_ubl", args=[obj.id])
        except Exception:
            return ""
        return format_html('<a class="button" href="{}">Download UBL XML</a>', url)
    download_ubl_button.short_description = "Download UBL"
