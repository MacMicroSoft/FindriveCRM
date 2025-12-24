import { Wrench, Phone, Mail, MapPin, Car } from 'lucide-react';
import { Service } from '../types';

interface ServiceListProps {
  services: Service[];
  onSelectService: (id: string) => void;
}

export function ServiceList({ services, onSelectService }: ServiceListProps) {
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 md:px-6">
        <h1 className="text-gray-900 flex items-center gap-2">
          <Wrench className="w-6 h-6" />
          Сервіси
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          Список СТО та автосервісів
        </p>
      </div>

      {/* Services List */}
      <div className="flex-1 overflow-auto p-4 md:p-6 space-y-3">
        {services.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Wrench className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Немає сервісів</p>
          </div>
        ) : (
          services.map(service => (
            <div
              key={service.id}
              onClick={() => onSelectService(service.id)}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Wrench className="w-5 h-5 text-blue-600" />
                  <h3 className="text-gray-900">{service.name}</h3>
                </div>
                {service.activeVehicles > 0 && (
                  <span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                    <Car className="w-3 h-3" />
                    {service.activeVehicles}
                  </span>
                )}
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <MapPin className="w-4 h-4" />
                  <span>{service.address}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Phone className="w-4 h-4" />
                  <span>{service.phone}</span>
                </div>
                {service.email && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Mail className="w-4 h-4" />
                    <span>{service.email}</span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
