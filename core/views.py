from django.shortcuts import render
from django.views.generic import ListView, CreateView
from .models import Transaction
from .forms import TransactionForm
import pandas as pd
import json
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime
from django.contrib.auth.decorators import login_required

# Create your views here.

class DashboardView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'core/home.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        # Obtener el parámetro de filtro
        period = self.request.GET.get('period', 'all')
        qs = super().get_queryset().filter(user=self.request.user).order_by('-date')
        
        # Aplicar filtros de fecha
        today = timezone.now().date()
        if period == 'week':
            start_date = today - timedelta(days=today.weekday())
            qs = qs.filter(date__gte=start_date)
        elif period == 'month':
            start_date = today.replace(day=1)
            qs = qs.filter(date__month=start_date.month, date__year=start_date.year)
        
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        
        # Calcular totales
        context['total_income'] = qs.filter(transaction_type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_expense'] = qs.filter(transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
        context['balance'] = context['total_income'] - context['total_expense']
        
        # Datos para el gráfico
        expenses = qs.filter(transaction_type='Expense')
        context['expense_categories'] = json.dumps(list(expenses.values_list('category_expense', flat=True)))
        # Convertir Decimal a float
        expense_amounts = [float(amount) for amount in expenses.values_list('amount', flat=True)]
        context['expense_amounts'] = json.dumps(expense_amounts)
        
        # Parámetro de periodo actual
        context['current_period'] = self.request.GET.get('period', 'all')
        
        return context


class TransactionCreateView(CreateView):
    form_class = TransactionForm
    template_name = 'core/transaction_form.html'
    success_url = '/home/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@login_required
def export_to_excel(request):
    # Get the current period filter
    period = request.GET.get('period', 'all')
    
    # Get transactions based on period filter
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    
    if period == 'week':
        start_date = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
        transactions = transactions.filter(date__gte=start_date)
    elif period == 'month':
        start_date = timezone.now().date().replace(day=1)
        transactions = transactions.filter(date__month=start_date.month, date__year=start_date.year)

    # Create DataFrame from transactions
    data = []
    for t in transactions:
        category = t.category_income if t.transaction_type == 'Income' else t.category_expense
        data.append({
            'Date': t.date,
            'Type': t.transaction_type,
            'Category': category,
            'Description': t.description,
            'Amount': t.amount
        })
    
    df = pd.DataFrame(data)
    
    # Calculate summary
    total_income = transactions.filter(transaction_type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # Calculate expense breakdown for pie chart
    expense_data = transactions.filter(transaction_type='Expense').values('category_expense').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Create Excel writer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write transactions starting from row 1
        df.to_excel(writer, sheet_name='Financial Report', startrow=1, index=False)
        
        # Get the workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Financial Report']
        
        # Add title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter'
        })
        worksheet.merge_range('A1:E1', 'Transaction History', title_format)
        
        # Format for currency
        currency_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'align': 'right'
        })
        
        # Format for headers
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'bg_color': '#f8f9fa',
            'border': 1,
            'align': 'center'
        })
        
        # Format column headers
        for col_num, value in enumerate(['Date', 'Type', 'Category', 'Description', 'Amount']):
            worksheet.write(1, col_num, value, header_format)
        
        # Format columns
        worksheet.set_column('A:A', 12)  # Date
        worksheet.set_column('B:B', 10)  # Type
        worksheet.set_column('C:C', 15)  # Category
        worksheet.set_column('D:D', 30)  # Description
        worksheet.set_column('E:E', 12, currency_format)  # Amount

        # Calculate last row of transactions
        last_row = len(df) + 2

        # Add summary section with a gap of 2 rows
        summary_start_row = last_row + 3
        summary_format = workbook.add_format({
            'bold': True,
            'font_size': 11
        })
        
        worksheet.write(summary_start_row, 0, 'Summary', workbook.add_format({
            'bold': True,
            'font_size': 12,
            'underline': True
        }))
        
        # Write summary data
        worksheet.write(summary_start_row + 1, 0, 'Total Income', summary_format)
        worksheet.write(summary_start_row + 1, 1, total_income, currency_format)
        
        worksheet.write(summary_start_row + 2, 0, 'Total Expenses', summary_format)
        worksheet.write(summary_start_row + 2, 1, total_expense, currency_format)
        
        worksheet.write(summary_start_row + 3, 0, 'Balance', summary_format)
        worksheet.write(summary_start_row + 3, 1, balance, currency_format)

        # Add expense breakdown chart
        if expense_data:
            # Create pie chart
            chart = workbook.add_chart({'type': 'pie'})
            
            # Write expense breakdown data
            breakdown_start_row = summary_start_row + 5
            worksheet.write(breakdown_start_row, 0, 'Expense Breakdown', workbook.add_format({
                'bold': True,
                'font_size': 12,
                'underline': True
            }))
            
            worksheet.write(breakdown_start_row + 1, 0, 'Category', header_format)
            worksheet.write(breakdown_start_row + 1, 1, 'Amount', header_format)
            
            row = breakdown_start_row + 2
            for item in expense_data:
                worksheet.write(row, 0, item['category_expense'])
                worksheet.write(row, 1, item['total'], currency_format)
                row += 1

            # Configure chart
            chart.add_series({
                'name': 'Expenses',
                'categories': f'=Financial Report!$A${breakdown_start_row + 2}:$A${row}',
                'values': f'=Financial Report!$B${breakdown_start_row + 2}:$B${row}',
                'data_labels': {
                    'value': True,
                    'category': True,
                    'percentage': True,
                    'position': 'outside_end',
                    'font': {'size': 9},
                    'separator': '\n',
                    'format': {'num_format': '0.0%'}
                }
            })

            chart.set_title({
                'name': 'Expense Distribution',
                'name_font': {'size': 12, 'bold': True}
            })
            chart.set_size({'width': 600, 'height': 400})  # Aumentar tamaño
            worksheet.insert_chart(breakdown_start_row + 1, 3, chart, {
                'x_offset': 25,
                'y_offset': 10
            })
            
            # Adding and configuring the legend
            chart.set_legend({
                'position': 'right',
                'font': {'size': 9},
                'layout': {
                    'x': 1.1,
                    'y': 0.25
                }
            })
            
            # Insert chart
            worksheet.insert_chart(breakdown_start_row + 1, 3, chart)

    # Generate response
    output.seek(0)
    filename = f'moneywise_report_{datetime.now().strftime("%Y%m%d")}.xlsx'
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response