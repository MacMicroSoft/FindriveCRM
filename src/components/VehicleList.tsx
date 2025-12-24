import { useState } from 'react';
import { Car, Plus, Search, Filter, Star } from 'lucide-react';
import { Vehicle } from '../types';

interface VehicleListProps {
  vehicles: Vehicle[];
  onSelectVehicle: (id: string) => void;
  onAddVehicle: () => void;
  onToggleSaved?: (id: string) => void;
}

export function VehicleList({ vehicles, onSelectVehicle, onAddVehicle, onToggleSaved }: VehicleListProps) {
  const [activeTab, setActiveTab] = useState<'active' | 'pending'>('active');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredVehicles = vehicles
    .filter(v => {
      if (activeTab === 'active') return v.isActive;
      return !v.isActive;
    })
    .filter(v => {
      const query = searchQuery.toLowerCase();
      return (
        v.licensePlate.toLowerCase().includes(query) ||
        v.brand.toLowerCase().includes(query) ||
        v.model.toLowerCase().includes(query) ||
        v.vin.toLowerCase().includes(query)
      );
    });

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
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-gray-900 flex items-center gap-2">
            <Car className="w-6 h-6" />
            Автопарк
          </h1>
          <button
            onClick={onAddVehicle}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            <span className="hidden md:inline">Додати авто</span>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setActiveTab('active')}
            className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
              activeTab === 'active'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Активні ({vehicles.filter(v => v.isActive).length})
          </button>
          <button
            onClick={() => setActiveTab('pending')}
            className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
              activeTab === 'pending'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Очікуючі ({vehicles.filter(v => !v.isActive).length})
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Пошук за номером, маркою, VIN..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Vehicle List */}
      <div className="flex-1 overflow-auto p-4 md:p-6 space-y-3">
        {filteredVehicles.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Car className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Немає автомобілів у цій категорії</p>
          </div>
        ) : (
          filteredVehicles.map(vehicle => (
            <div
              key={vehicle.id}
              onClick={() => onSelectVehicle(vehicle.id)}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-gray-900">{vehicle.brand} {vehicle.model}</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(vehicle.status)}`}>
                      {getStatusLabel(vehicle.status)}
                    </span>
                  </div>
                  <p className="text-gray-600">{vehicle.licensePlate}</p>
                </div>
                <span className="text-gray-500 text-sm">{vehicle.year}</span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">VIN: {vehicle.vin}</span>
                {onToggleSaved && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleSaved(vehicle.id);
                    }}
                    className="text-gray-500 hover:text-yellow-500"
                  >
                    <Star className={`w-5 h-5 ${vehicle.isSaved ? 'text-yellow-500 fill-yellow-500' : ''}`} />
                  </button>
                )}
              </div>

              {vehicle.ownerName && (
                <div className="mt-2 pt-2 border-t border-gray-100">
                  <p className="text-sm text-gray-600">
                    Власник: <span className="text-gray-900">{vehicle.ownerName}</span>
                  </p>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}