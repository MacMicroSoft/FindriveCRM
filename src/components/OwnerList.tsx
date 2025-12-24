import { useState } from 'react';
import { Users, Plus, Search, Mail, Phone } from 'lucide-react';
import { Owner } from '../types';

interface OwnerListProps {
  owners: Owner[];
  onAddOwner: () => void;
}

export function OwnerList({ owners, onAddOwner }: OwnerListProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredOwners = owners.filter(owner => {
    const query = searchQuery.toLowerCase();
    return (
      owner.name.toLowerCase().includes(query) ||
      owner.email.toLowerCase().includes(query) ||
      owner.phone.includes(query)
    );
  });

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 md:px-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-gray-900 flex items-center gap-2">
            <Users className="w-6 h-6" />
            Власники
          </h1>
          <button
            onClick={onAddOwner}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            <span className="hidden md:inline">Додати власника</span>
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Пошук за ім'ям, email або телефоном..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Owner List */}
      <div className="flex-1 overflow-auto p-4 md:p-6 space-y-3">
        {filteredOwners.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Немає власників</p>
          </div>
        ) : (
          filteredOwners.map(owner => (
            <div
              key={owner.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-gray-900 mb-1">{owner.name}</h3>
                  {owner.telegramUsername && (
                    <p className="text-sm text-blue-600">
                      Telegram: {owner.telegramUsername}
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <span className="text-sm text-gray-600">Активних авто:</span>
                  <p className="text-blue-600">{owner.activeVehicles}</p>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-gray-600">
                  <Mail className="w-4 h-4" />
                  <span className="text-sm">{owner.email}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Phone className="w-4 h-4" />
                  <span className="text-sm">{owner.phone}</span>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-gray-100">
                <p className="text-xs text-gray-500">
                  Додано: {new Date(owner.createdAt).toLocaleDateString('uk-UA')}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
