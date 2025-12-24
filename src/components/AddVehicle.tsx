import { useState } from 'react';
import { ArrowLeft, Car } from 'lucide-react';
import { Owner } from '../types';

interface AddVehicleProps {
  owners: Owner[];
  onBack: () => void;
  onAdd: (data: {
    vin: string;
    licensePlate: string;
    brand: string;
    model: string;
    year: number;
    ownerId: string | null;
    isActive: boolean;
  }) => void;
}

export function AddVehicle({ owners, onBack, onAdd }: AddVehicleProps) {
  const [vin, setVin] = useState('');
  const [licensePlate, setLicensePlate] = useState('');
  const [brand, setBrand] = useState('');
  const [model, setModel] = useState('');
  const [year, setYear] = useState('');
  const [ownerId, setOwnerId] = useState<string>('');
  const [isActive, setIsActive] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!vin || !licensePlate || !brand || !model || !year) {
      alert('Будь ласка, заповніть всі обов\'язкові поля');
      return;
    }

    onAdd({
      vin,
      licensePlate,
      brand,
      model,
      year: parseInt(year),
      ownerId: ownerId || null,
      isActive
    });
  };

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
            <Car className="w-6 h-6" />
            Додати новий автомобіль
          </h1>
        </div>
      </div>

      {/* Form */}
      <div className="flex-1 overflow-auto p-4 md:p-6">
        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto space-y-4">
          <div className="bg-white rounded-lg p-4 md:p-6 border border-gray-200 space-y-4">
            <h3 className="text-gray-900">Основна інформація</h3>

            <div>
              <label className="block text-gray-700 mb-1">VIN номер *</label>
              <input
                type="text"
                value={vin}
                onChange={(e) => setVin(e.target.value)}
                placeholder="WBADT43452G123456"
                className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-gray-700 mb-1">Номерний знак *</label>
              <input
                type="text"
                value={licensePlate}
                onChange={(e) => setLicensePlate(e.target.value)}
                placeholder="AA 1234 BB"
                className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 mb-1">Марка *</label>
                <input
                  type="text"
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  placeholder="BMW"
                  className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-gray-700 mb-1">Модель *</label>
                <input
                  type="text"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  placeholder="320d"
                  className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-gray-700 mb-1">Рік випуску *</label>
              <input
                type="number"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                placeholder="2020"
                min="1990"
                max={new Date().getFullYear() + 1}
                className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 md:p-6 border border-gray-200 space-y-4">
            <h3 className="text-gray-900">Додаткова інформація</h3>

            <div>
              <label className="block text-gray-700 mb-1">Власник</label>
              <select
                value={ownerId}
                onChange={(e) => setOwnerId(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Без власника</option>
                {owners.map(owner => (
                  <option key={owner.id} value={owner.id}>
                    {owner.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isActive}
                  onChange={(e) => setIsActive(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-gray-700">
                  Активне авто (здане в лізинг)
                </span>
              </label>
              <p className="text-sm text-gray-500 mt-1">
                Якщо не вибрано, авто потрапить у категорію "Очікуючі"
              </p>
            </div>
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
              Додати автомобіль
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
