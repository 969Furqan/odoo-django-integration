from django.urls import path
from .views import invoice_fields_view, download_ubl_xml


urlpatterns = [
    # path('invoice-fields/', invoice_fields_view, name='invoice_fields'),
    path('invoices/<int:pk>/download-ubl/', download_ubl_xml, name='invoice_download_ubl'),
]


