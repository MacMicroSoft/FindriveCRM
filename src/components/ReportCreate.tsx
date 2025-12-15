import { useState } from 'react';
import { ArrowLeft, FileText, Plus } from 'lucide-react';
import { Vehicle, Service } from '../types';

interface ReportCreateProps {
  vehicles: Vehicle[];
  services: Service[];
  onBack: () => void;
  onCreate: (data: {
    vehicleId: string;
    expenseType: 'service' | 'other';
    serviceId?: string;
    serviceName?: string;
    category: string;
    subcategory?: string;
    customSubcategory?: string;
    description: string;
    priceType: 'total' | 'quantity';
    totalAmount?: number;
    unitPrice?: number;
    quantity?: number;
    date: Date;
  }) => void;
}

const subcategories = {
  fuel: 'Паливо',
  parts: 'Запчастини',
  documents: 'Документи',
  custom: 'Інше'
};

export function ReportCreate({ vehicles, services, onBack, onCreate }: ReportCreateProps) {
  const [vehicleId, setVehicleId] = useState('');
  const [expenseType, setExpenseType] = useState<'service' | 'other'>('other');
  const [serviceId, setServiceId] = useState('');
  const [customServiceName, setCustomServiceName] = useState('');
  const [category, setCategory] = useState('Others');
  const [subcategory, setSubcategory] = useState<string>('');
  const [customSubcategory, setCustomSubcategory] = useState('');
  const [description, setDescription] = useState('');
  const [priceType, setPriceType] = useState<'total' | 'quantity'>('total');
  const [totalAmount, setTotalAmount] = useState('');
  const [unitPrice, setUnitPrice] = useState('');
  const [quantity, setQuantity] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!vehicleId || !description) {
      alert('Будь ласка, заповніть всі обов\'язкові поля');
      return;
    }

    if (expenseType === 'service' && !serviceId && !customServiceName.trim()) {
      alert('Будь ласка, оберіть або введіть назву сервісу');
      return;
    }

    if (expenseType === 'other' && !subcategory) {
      alert('Будь ласка, оберіть підкатегорію');
      return;
    }

    if (subcategory === 'custom' && !customSubcategory.trim()) {
      alert('Будь ласка, вкажіть власну підкатегорію');
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

    const selectedService = serviceId ? services.find(s => s.id === serviceId) : null;

    onCreate({
      vehicleId,
      expenseType,
      serviceId: serviceId || undefined,
      serviceName: serviceId ? selectedService?.name : (customServiceName || undefined),
      category: expenseType === 'service' ? 'Service' : category,
      subcategory: subcategory !== 'custom' ? subcategory : undefined,
      customSubcategory: subcategory === 'custom' ? customSubcategory : undefined,
      description,
      priceType,
      totalAmount: priceType === 'total' ? parseFloat(totalAmount) : undefined,
      unitPrice: priceType === 'quantity' ? parseFloat(unitPrice) : undefined,
      quantity: priceType === 'quantity' ? parseFloat(quantity) : undefined,
      date: new Date(date)
    });
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
            Додати витрату
          </h1>
        </div>
      </div>

      {/* Form */}
      <div className="flex-1 overflow-auto p-4 md:p-6">
        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto space-y-4">
          <div className="bg-white rounded-lg p-4 md:p-6 border border-gray-200 space-y-4">
            <h3 className="text-gray-900">Основна інформація</h3>

            <div>
              <label className="block text-gray-700 mb-1">Автомобіль *</label>
              <select
                value={vehicleId}
                onChange={(e) => setVehicleId(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Оберіть автомобіль</option>
                {vehicles.map(vehicle => (
                  <option key={vehicle.id} value={vehicle.id}>
                    {vehicle.brand} {vehicle.model} - {vehicle.licensePlate}
                  </option>
                ))}
              </select>
            </div>

            {/* Тип витрати */}
            <div>
              <label className="block text-gray-700 mb-2">Тип витрати *</label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setExpenseType('other')}
                  className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
                    expenseType === 'other'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Other
                </button>
                <button
                  type="button"
                  onClick={() => setExpenseType('service')}
                  className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
                    expenseType === 'service'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Service
                </button>
              </div>
            </div>

            {/* Service Section */}
            {expenseType === 'service' && (
              <div className="space-y-3">
                <div>
                  <label className="block text-gray-700 mb-1">Сервіс</label>
                  <select
                    value={serviceId}
                    onChange={(e) => {
                      setServiceId(e.target.value);
                      if (e.target.value) setCustomServiceName('');
                    }}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Оберіть сервіс зі списку</option>
                    {services.map(service => (
                      <option key={service.id} value={service.id}>
                        {service.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <div className="flex-1 border-t border-gray-300"></div>
                  <span className="text-sm text-gray-500">або</span>
                  <div className="flex-1 border-t border-gray-300"></div>
                </div>

                <div>
                  <label className="block text-gray-700 mb-1">Введіть назву сервісу вручну</label>
                  <input
                    type="text"
                    value={customServiceName}
                    onChange={(e) => {
                      setCustomServiceName(e.target.value);
                      if (e.target.value) setServiceId('');
                    }}
                    placeholder="Назва сервісу"
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={!!serviceId}
                  />
                </div>
              </div>
            )}

            {/* Others Section */}
            {expenseType === 'other' && (
              <div>
                <label className="block text-gray-700 mb-1">Підкатегорія *</label>
                <select
                  value={subcategory}
                  onChange={(e) => setSubcategory(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Оберіть підкатегорію</option>
                  {Object.entries(subcategories).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>
            )}

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
              onClick={onBack}
              className="flex-1 bg-gray-200 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Скасувати
            </button>
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Додати витрату
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
