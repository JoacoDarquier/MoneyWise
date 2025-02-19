document.addEventListener('DOMContentLoaded', function() {
    // Código existente para las transacciones
    const transactionTypeRadios = document.querySelectorAll('input[name="transaction_type"]');
    const incomeCategories = document.getElementById('income-categories');
    const expenseCategories = document.getElementById('expense-categories');

    function updateCategories() {
        // Obtener el radio seleccionado
        const selectedRadio = document.querySelector('input[name="transaction_type"]:checked');
        
        // Verificar si hay algún radio seleccionado
        if (!selectedRadio) {
            incomeCategories.style.display = 'none';
            expenseCategories.style.display = 'none';
            return;
        }

        const selectedType = selectedRadio.value;
        incomeCategories.style.display = selectedType === 'Income' ? 'block' : 'none';
        expenseCategories.style.display = selectedType === 'Expense' ? 'block' : 'none';
    }

    // Forzar selección inicial si ningún radio está seleccionado
    if (!document.querySelector('input[name="transaction_type"]:checked')) {
        document.getElementById('income-type').checked = true;
    }

    transactionTypeRadios.forEach(radio => {
        radio.addEventListener('change', updateCategories);
    });

    // Ejecutar inicialización
    updateCategories();
});