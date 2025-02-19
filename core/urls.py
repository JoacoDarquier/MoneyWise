from django.urls import path

from core.views import *

urlpatterns = [
    path('home/', DashboardView.as_view(), name='home'),
    path('add-transaction/', TransactionCreateView.as_view(), name='add-transaction'),
    path('export-excel/', export_to_excel, name='export-excel'),
]