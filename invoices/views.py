from django.http import JsonResponse
from .odoo_client import fetch_invoice_field_names


def invoice_fields_view(_request):
    try:
        names = fetch_invoice_field_names()
        return JsonResponse({
            'ok': True,
            'count': len(names),
            'fields': names,
        })
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)

# Create your views here.
