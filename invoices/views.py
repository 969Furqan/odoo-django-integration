import base64
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from .odoo_client import fetch_invoice_field_names
from .models import OdooInvoice


def invoice_fields_view(_request):
    try:
        names = fetch_invoice_field_names()
        return JsonResponse({
            'ok': True,
            'count': len(names),
            'fields': names,
        })
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)

# Create your views here.


def download_ubl_xml(_request, pk):
    invoice = get_object_or_404(OdooInvoice, pk=pk)
    data = invoice.data or {}
    b64_content = data.get("ubl_cii_xml_file") or data.get("ubl_xml_file")
    filename = data.get("ubl_cii_xml_filename") or data.get("ubl_xml_filename") or f"{invoice.name or 'invoice'}_ubl.xml"
    if not b64_content:
        raise Http404("UBL export not available for this invoice")

    try:
        xml_bytes = base64.b64decode(b64_content)
    except Exception:
        raise Http404("Invalid UBL content")

    response = HttpResponse(xml_bytes, content_type="application/xml")
    response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
    return response
