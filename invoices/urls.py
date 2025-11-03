from django.urls import path
from .views import invoice_fields_view


urlpatterns = [
    path('invoice-fields/', invoice_fields_view, name='invoice_fields'),
]


