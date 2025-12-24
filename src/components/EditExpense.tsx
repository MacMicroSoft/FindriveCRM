import { useState } from 'react';
import { ArrowLeft, FileText, Trash2 } from 'lucide-react';
import { Expense, Vehicle } from '../types';

interface EditExpenseProps {
  expense: Expense;
  vehicles: Vehicle[];
  onBack: () => void;
  onUpdate: (id: string, data: Partial<Expense>) => void;
  onDelete: (id: string) => void;
}

const subcategories = {
  fuel: 'Паливо',
  parts: 'Запчастини',
  documents: 'Документи',
  custom: 'Інше'
};

export function EditExpense({ expense, vehicles, onBack, onUpdate, onDelete }: EditExpenseProps) {
  const [description, setDescription] = useState(expense.description);
  const [subcategory, setSubcategory] = useState(expense.subcategory || expense.customSubcategory ? 'custom' : '');
  const [customSubcategory, setCustomSubcategory] = useState(expense.customSubcategory || '');
  const [priceType, setPriceType] = useState<'total' | 'quantity'>(expense.priceType);
  const [totalAmount, setTotalAmount] = useState(expense.totalAmount?.toString() || '');
  const [unitPrice, setUnitPrice] = useState(expense.unitPrice?.toString() || '');
  const [quantity, setQuantity] = useState(expense.quantity?.toString() || '');
  const [date, setDate] = useState(new Date(expense.date).toISOString().split('T')[0]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const vehicle = vehicles.find(v => v.id === expense.vehicleId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!description) {
      alert('Будь ласка, введіть опис');
      return;
    }

    if (priceType === 'total' && !totalAmount) {
      alert('Будь ласка, вкажіть загальну суму');
      return;
    }

    if (priceType === 'quantity' && (!unitPrice || !quantity)) {
      alert('Будь ласка, вкажіть ціну та кількість');
      return;
    }

    onUpdate(expense.id, {
      description,
      subcategory: subcategory !== 'custom' ? subcategory : undefined,
      customSubcategory: subcategory === 'custom' ? customSubcategory : undefined,
      priceType,
      totalAmount: priceType === 'total' ? parseFloat(totalAmount) : undefined,
      unitPrice: priceType === 'quantity' ? parseFloat(unitPrice) : undefined,
      quantity: priceType === 'quantity' ? parseFloat(quantity) : undefined,
      date: new Date(date)
    });
  };

  const handleDelete = () => {
    onDelete(expense.id);
    onBack();
  };

  const calculatedTotal = priceType === 'quantity' && unitPrice && quantity
    ? (parseFloat(unitPrice) * parseFloat(quantity)).toFixed(2)
    : null;

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 md:px-6">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-gray-900 flex items-center gap-2">
            <FileText className="w-6 h-6" />
            Редагувати витрату
          </h1>
        </div>
      </div>

      {/* Form */}
      <div className="flex-1 overflow-auto p-4 md:p-6">
        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto space-y-4">
          <div className="bg-white rounded-lg p-4 md:p-6 border border-gray-200 space-y-4">
            <h3 className="text-gray-900">Інформація</h3>

            <div>
              <label className="block text-gray-700 mb-1">Автомобіль</label>
              <input
                type="text"
                value={vehicle ? `${vehicle.brand} ${vehicle.model} - ${vehicle.licensePlate}` : 'Невідомо'}
                disabled
                className="w-full p-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600"
              />
            </div>

            <div>
              <label className="block text-gray-700 mb-1">Підкатегорія</label>
              <select
                value={subcategory}
                onChange={(e) => setSubcategory(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Оберіть підкатегорію</option>
                {Object.entries(subcategories).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </select>
            </div>

            {subcategory === 'custom' && (
              <div>
                <label className="block text-gray-700 mb-1">Власна підкатегорія *</label>
                <input
                  type="text"
                  value={customSubcategory}
                  onChange={(e) => setCustomSubcategory(e.target.value)}
                  placeholder="Введіть назву підкатегорії"
                  className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-gray-700 mb-1">Опис *</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Детальний опис витрати"
                className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                required
              />
            </div>

            <div>
              <label className="block text-gray-700 mb-1">Дата *</label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 md:p-6 border border-gray-200 space-y-4">
            <h3 className="text-gray-900">Вартість (PLN)</h3>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setPriceType('total')}
                className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
                  priceType === 'total'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Загальна сума
              </button>
              <button
                type="button"
                onClick={() => setPriceType('quantity')}
                className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
                  priceType === 'quantity'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Ціна × Кількість
              </button>
            </div>

            {priceType === 'total' ? (
              <div>
                <label className="block text-gray-700 mb-1">Загальна сума (PLN) *</label>
                <input
                  type="number"
                  step="0.01"
                  value={totalAmount}
                  onChange={(e) => setTotalAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            ) : (
              <>
                <div>
                  <label className="block text-gray-700 mb-1">Ціна за одиницю (PLN) *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={unitPrice}
                    onChange={(e) => setUnitPrice(e.target.value)}
                    placeholder="0.00"
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-gray-700 mb-1">Кількість *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    placeholder="0"
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                {calculatedTotal && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <p className="text-sm text-gray-700">Загальна сума:</p>
                    <p className="text-blue-900">{calculatedTotal} PLN</p>
                  </div>
                )}
              </>
            )}
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => setShowDeleteConfirm(true)}
              className="bg-red-600 text-white p-3 rounded-lg hover:bg-red-700 transition-colors"
            >
              <Trash2 className="w-5 h-5" />
            </button>
            <button
              type="button"
              onClick={onBack}
              className="flex-1 bg-gray-200 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Скасувати
            </button>
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Зберегти зміни
            </button>
          </div>
        </form>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full">
            <h3 className="text-gray-900 mb-3">Видалити витрату?</h3>
            <p className="text-gray-600 mb-6">
              Цю дію неможливо буде скасувати
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Скасувати
              </button>
              <button
                onClick={handleDelete}
                className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors"
              >
                Видалити
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
