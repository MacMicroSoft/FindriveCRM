import { ArrowLeft, Wrench, Phone, Mail, MapPin, Car, Calendar } from 'lucide-react';
import { Service, Vehicle, Expense } from '../types';

interface ServiceDetailsProps {
  service: Service;
  vehicles: Vehicle[];
  expenses: Expense[];
  onBack: () => void;
  onSelectVehicle: (id: string) => void;
}

export function ServiceDetails({ service, vehicles, expenses, onBack, onSelectVehicle }: ServiceDetailsProps) {
  // Знаходимо всі авто що обслуговуються в цьому сервісі
  const serviceExpenses = expenses.filter(e => e.serviceId === service.id);
  const vehicleIds = [...new Set(serviceExpenses.map(e => e.vehicleId))];
  const serviceVehicles = vehicles.filter(v => vehicleIds.includes(v.id));

  // Розрахунок витрат
  const totalExpenses = serviceExpenses.reduce((sum, expense) => {
    const amount = expense.totalAmount || (expense.unitPrice && expense.quantity ? expense.unitPrice * expense.quantity : 0);
    return sum + amount;
  }, 0);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 md:px-6">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-3"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Назад до сервісів</span>
        </button>
        <div className="flex items-center gap-3">
          <Wrench className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-gray-900">{service.name}</h1>
            <p className="text-sm text-gray-600">
              {serviceVehicles.length} {serviceVehicles.length === 1 ? 'авто' : 'авто'} на обслуговуванні
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4 md:p-6">
        {/* Service Info */}
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
          <h2 className="text-gray-900 mb-3">Контактна інформація</h2>
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2 text-gray-600">
              <MapPin className="w-4 h-4" />
              <span>{service.address}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-600">
              <Phone className="w-4 h-4" />
              <a href={`tel:${service.phone}`} className="hover:text-blue-600">
                {service.phone}
              </a>
            </div>
            {service.email && (
              <div className="flex items-center gap-2 text-gray-600">
                <Mail className="w-4 h-4" />
                <a href={`mailto:${service.email}`} className="hover:text-blue-600">
                  {service.email}
                </a>
              </div>
            )}
          </div>

          {/* Total Expenses */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Загальні витрати:</span>
              <span className="text-gray-900">{totalExpenses.toFixed(2)} PLN</span>
            </div>
          </div>
        </div>

        {/* Vehicles */}
        <div className="mb-4">
          <h2 className="text-gray-900 mb-3">Автомобілі на обслуговуванні</h2>
          {serviceVehicles.length === 0 ? (
            <div className="bg-white border border-gray-200 rounded-lg p-8 text-center text-gray-500">
              <Car className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>Немає автомобілів на обслуговуванні</p>
            </div>
          ) : (
            <div className="space-y-3">
              {serviceVehicles.map(vehicle => {
                const vehicleExpenses = serviceExpenses.filter(e => e.vehicleId === vehicle.id);
                const lastService = vehicleExpenses.sort((a, b) => 
                  new Date(b.date).getTime() - new Date(a.date).getTime()
                )[0];
                const vehicleTotal = vehicleExpenses.reduce((sum, expense) => {
                  const amount = expense.totalAmount || (expense.unitPrice && expense.quantity ? expense.unitPrice * expense.quantity : 0);
                  return sum + amount;
                }, 0);

                return (
                  <div
                    key={vehicle.id}
                    onClick={() => onSelectVehicle(vehicle.id)}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-gray-900">
                          {vehicle.brand} {vehicle.model}
                        </h3>
                        <p className="text-gray-600 text-sm">{vehicle.licensePlate}</p>
                      </div>
                      <span className="text-blue-600">{vehicleTotal.toFixed(2)} PLN</span>
                    </div>

                    {lastService && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Calendar className="w-4 h-4" />
                        <span>Останній візит: {new Date(lastService.date).toLocaleDateString('uk-UA')}</span>
                      </div>
                    )}

                    {vehicle.ownerName && (
                      <div className="mt-2 text-sm text-gray-600">
                        Власник: {vehicle.ownerName}
                      </div>
                    )}

                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <p className="text-xs text-gray-500">
                        {vehicleExpenses.length} {vehicleExpenses.length === 1 ? 'візит' : 'візитів'}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
