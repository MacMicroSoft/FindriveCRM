import { Star, Car, ArrowLeft } from 'lucide-react';
import { Vehicle } from '../types';

interface SavedVehiclesProps {
  vehicles: Vehicle[];
  onSelectVehicle: (id: string) => void;
  onToggleSaved: (id: string) => void;
  onBack: () => void;
}

export function SavedVehicles({ vehicles, onSelectVehicle, onToggleSaved, onBack }: SavedVehiclesProps) {
  const savedVehicles = vehicles.filter(v => v.isSaved);

  const getStatusLabel = (status: Vehicle['status']) => {
    const labels = {
      'processing': 'В Обробці',
      'pending-approval': 'На узгодженні',
      'approved': 'Узгоджено',
      'active': 'Активне',
      'maintenance': 'Ремонт'
    };
    return labels[status];
  };

  const getStatusColor = (status: Vehicle['status']) => {
    const colors = {
      'processing': 'bg-blue-100 text-blue-700',
      'pending-approval': 'bg-yellow-100 text-yellow-700',
      'approved': 'bg-green-100 text-green-700',
      'active': 'bg-emerald-100 text-emerald-700',
      'maintenance': 'bg-orange-100 text-orange-700'
    };
    return colors[status];
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 md:px-6">
        <h1 className="text-gray-900 flex items-center gap-2">
          <Star className="w-6 h-6 text-yellow-500 fill-yellow-500" />
          Збережені авто
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          Важливі автомобілі для швидкого доступу
        </p>
      </div>

      {/* Saved Vehicles List */}
      <div className="flex-1 overflow-auto p-4 md:p-6 space-y-3">
        {savedVehicles.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Star className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Немає збережених автомобілів</p>
            <p className="text-sm mt-1">
              Натисніть зірочку на авто щоб додати його сюди
            </p>
          </div>
        ) : (
          savedVehicles.map(vehicle => (
            <div
              key={vehicle.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all"
            >
              <div className="flex items-start gap-3">
                <button
                  onClick={() => onToggleSaved(vehicle.id)}
                  className="mt-1"
                >
                  <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                </button>
                
                <div 
                  className="flex-1 cursor-pointer"
                  onClick={() => onSelectVehicle(vehicle.id)}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-gray-900">{vehicle.brand} {vehicle.model}</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(vehicle.status)}`}>
                      {getStatusLabel(vehicle.status)}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-2">{vehicle.licensePlate}</p>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">{vehicle.year}</span>
                    {vehicle.ownerName && (
                      <span className="text-gray-600">
                        {vehicle.ownerName}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}