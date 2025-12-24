import { useState } from 'react';
import { FileText, Upload, Eye, Edit2, Search } from 'lucide-react';
import { Expense, Invoice, Vehicle } from '../types';

interface InvoiceListProps {
  expenses: Expense[];
  invoices: Invoice[];
  vehicles: Vehicle[];
  onEditExpense: (expenseId: string) => void;
  onUploadInvoice: (expenseId: string, file: File) => void;
  onCreateExpense: () => void;
}

export function InvoiceList({ expenses, invoices, vehicles, onEditExpense, onUploadInvoice, onCreateExpense }: InvoiceListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');

  const filteredExpenses = expenses.filter(expense => {
    const vehicle = vehicles.find(v => v.id === expense.vehicleId);
    const query = searchQuery.toLowerCase();
    
    const matchesSearch = (
      expense.description.toLowerCase().includes(query) ||
      vehicle?.licensePlate.toLowerCase().includes(query) ||
      (vehicle?.brand + ' ' + vehicle?.model).toLowerCase().includes(query)
    );

    const matchesCategory = filterCategory === 'all' || 
      expense.subcategory === filterCategory ||
      expense.customSubcategory?.toLowerCase() === filterCategory.toLowerCase();

    return matchesSearch && matchesCategory;
  });

  const getSubcategoryLabel = (expense: Expense) => {
    const labels: Record<string, string> = {
      fuel: 'Паливо',
      parts: 'Запчастини',
      documents: 'Документи'
    };
    return expense.subcategory 
      ? labels[expense.subcategory] || expense.subcategory
      : expense.customSubcategory || 'Інше';
  };

  const getExpenseTotal = (expense: Expense) => {
    if (expense.priceType === 'total') {
      return expense.totalAmount || 0;
    } else {
      return (expense.unitPrice || 0) * (expense.quantity || 0);
    }
  };

  const handleFileUpload = (expenseId: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUploadInvoice(expenseId, file);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 md:px-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-gray-900 flex items-center gap-2">
            <FileText className="w-6 h-6" />
            Витрати та фактури
          </h1>
          <button
            onClick={onCreateExpense}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors hidden md:flex items-center gap-2"
          >
            <FileText className="w-5 h-5" />
            Додати витрату
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-3">
          <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Пошук за описом або автомобілем..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Category Filter */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {[
            { value: 'all', label: 'Всі' },
            { value: 'fuel', label: 'Паливо' },
            { value: 'parts', label: 'Запчастини' },
            { value: 'documents', label: 'Документи' }
          ].map(category => (
            <button
              key={category.value}
              onClick={() => setFilterCategory(category.value)}
              className={`px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                filterCategory === category.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category.label}
            </button>
          ))}
        </div>
      </div>

      {/* Expense List */}
      <div className="flex-1 overflow-auto p-4 md:p-6 space-y-3">
        {filteredExpenses.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Немає витрат</p>
          </div>
        ) : (
          filteredExpenses.map(expense => {
            const vehicle = vehicles.find(v => v.id === expense.vehicleId);
            const invoice = invoices.find(i => i.expenseId === expense.id);

            return (
              <div
                key={expense.id}
                className="bg-white border border-gray-200 rounded-lg p-4"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-gray-900">{expense.description}</span>
                      <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700">
                        {getSubcategoryLabel(expense)}
                      </span>
                    </div>
                    {vehicle && (
                      <p className="text-sm text-gray-600">
                        {vehicle.brand} {vehicle.model} - {vehicle.licensePlate}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-gray-900">{getExpenseTotal(expense).toFixed(2)} PLN</p>
                    <p className="text-xs text-gray-500">
                      {new Date(expense.date).toLocaleDateString('uk-UA')}
                    </p>
                  </div>
                </div>

                {/* Expense Details */}
                {expense.priceType === 'quantity' && (
                  <div className="text-sm text-gray-600 mb-3">
                    {expense.unitPrice} PLN × {expense.quantity} = {getExpenseTotal(expense).toFixed(2)} PLN
                  </div>
                )}

                {/* Invoice Section */}
                <div className="flex items-center gap-2 pt-3 border-t border-gray-100">
                  {invoice ? (
                    <>
                      <FileText className="w-4 h-4 text-green-600" />
                      <span className="text-sm text-gray-700 flex-1">
                        {invoice.fileName || invoice.number}
                      </span>
                      <button
                        onClick={() => alert('Перегляд фактури (функція для прикладу)')}
                        className="text-blue-600 hover:text-blue-700 p-1"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </>
                  ) : (
                    <>
                      <label className="flex-1 flex items-center gap-2 text-sm text-gray-600 cursor-pointer hover:text-gray-900 transition-colors">
                        <Upload className="w-4 h-4" />
                        <span>Завантажити фактуру</span>
                        <input
                          type="file"
                          accept=".pdf,.jpg,.jpeg,.png"
                          onChange={(e) => handleFileUpload(expense.id, e)}
                          className="hidden"
                        />
                      </label>
                    </>
                  )}
                  <button
                    onClick={() => onEditExpense(expense.id)}
                    className="text-gray-600 hover:text-gray-900 p-1"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}