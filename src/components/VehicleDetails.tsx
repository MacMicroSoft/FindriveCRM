import { useState } from 'react';
import { ArrowLeft, Car, Calendar, Edit2, Plus, CheckCircle, Circle, Trash2, MessageSquare } from 'lucide-react';
import { Vehicle, MaintenancePlan, Comment, Owner } from '../types';

interface VehicleDetailsProps {
  vehicle: Vehicle;
  maintenancePlans: MaintenancePlan[];
  comments: Comment[];
  owners: Owner[];
  onBack: () => void;
  onUpdateStatus: (vehicleId: string, newStatus: Vehicle['status']) => void;
  onChangeOwner: (vehicleId: string, ownerId: string | null) => void;
  onAddMaintenancePlan: (vehicleId: string, task: string, description: string, date: Date) => void;
  onToggleMaintenancePlan: (planId: string) => void;
  onDeleteMaintenancePlan: (planId: string) => void;
  onAddComment: (vehicleId: string, text: string) => void;
}

export function VehicleDetails({
  vehicle,
  maintenancePlans,
  comments,
  owners,
  onBack,
  onUpdateStatus,
  onChangeOwner,
  onAddMaintenancePlan,
  onToggleMaintenancePlan,
  onDeleteMaintenancePlan,
  onAddComment
}: VehicleDetailsProps) {
  const [activeTab, setActiveTab] = useState<'info' | 'maintenance' | 'comments'>('info');
  const [showOwnerSelect, setShowOwnerSelect] = useState(false);
  const [showAddMaintenance, setShowAddMaintenance] = useState(false);
  const [newMaintenanceTask, setNewMaintenanceTask] = useState('');
  const [newMaintenanceDesc, setNewMaintenanceDesc] = useState('');
  const [newMaintenanceDate, setNewMaintenanceDate] = useState('');
  const [newComment, setNewComment] = useState('');

  const vehiclePlans = maintenancePlans.filter(p => p.vehicleId === vehicle.id);
  const vehicleComments = comments.filter(c => c.vehicleId === vehicle.id);

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

  const handleStatusChange = () => {
    if (vehicle.status === 'processing') {
      onUpdateStatus(vehicle.id, 'pending-approval');
    }
  };

  const handleAddMaintenance = () => {
    if (newMaintenanceTask && newMaintenanceDate) {
      onAddMaintenancePlan(
        vehicle.id,
        newMaintenanceTask,
        newMaintenanceDesc,
        new Date(newMaintenanceDate)
      );
      setNewMaintenanceTask('');
      setNewMaintenanceDesc('');
      setNewMaintenanceDate('');
      setShowAddMaintenance(false);
    }
  };

  const handleAddComment = () => {
    if (newComment.trim()) {
      onAddComment(vehicle.id, newComment);
      setNewComment('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 md:px-6">
        <div className="flex items-center gap-3 mb-3">
          <button
            onClick={onBack}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-gray-900">{vehicle.brand} {vehicle.model}</h1>
            <p className="text-gray-600">{vehicle.licensePlate}</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('info')}
            className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
              activeTab === 'info'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Інформація
          </button>
          <button
            onClick={() => setActiveTab('maintenance')}
            className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
              activeTab === 'maintenance'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            План ремонту
          </button>
          <button
            onClick={() => setActiveTab('comments')}
            className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
              activeTab === 'comments'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Коментарі
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4 md:p-6">
        {/* Info Tab */}
        {activeTab === 'info' && (
          <div className="space-y-4">
            {/* Basic Info */}
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <h3 className="text-gray-900 mb-3">Основна інформація</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">VIN:</span>
                  <span className="text-gray-900">{vehicle.vin}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Рік випуску:</span>
                  <span className="text-gray-900">{vehicle.year}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Статус:</span>
                  <span className="text-gray-900">{getStatusLabel(vehicle.status)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Категорія:</span>
                  <span className="text-gray-900">{vehicle.isActive ? 'Активне' : 'Очікуюче'}</span>
                </div>
              </div>

              {/* Status Change Button */}
              {vehicle.status === 'processing' && (
                <button
                  onClick={handleStatusChange}
                  className="w-full mt-4 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Перевести на узгодження
                </button>
              )}
            </div>

            {/* Owner */}
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-gray-900">Власник</h3>
                <button
                  onClick={() => setShowOwnerSelect(!showOwnerSelect)}
                  className="text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  <Edit2 className="w-4 h-4" />
                  Змінити
                </button>
              </div>

              {showOwnerSelect ? (
                <select
                  value={vehicle.ownerId || ''}
                  onChange={(e) => {
                    onChangeOwner(vehicle.id, e.target.value || null);
                    setShowOwnerSelect(false);
                  }}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Без власника</option>
                  {owners.map(owner => (
                    <option key={owner.id} value={owner.id}>
                      {owner.name}
                    </option>
                  ))}
                </select>
              ) : (
                <p className="text-gray-600">
                  {vehicle.ownerName || 'Не призначено'}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Maintenance Tab */}
        {activeTab === 'maintenance' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-gray-900">План ремонту та обслуговування</h3>
              <button
                onClick={() => setShowAddMaintenance(!showAddMaintenance)}
                className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>

            {showAddMaintenance && (
              <div className="bg-white rounded-lg p-4 border border-gray-200 space-y-3">
                <input
                  type="text"
                  placeholder="Назва роботи"
                  value={newMaintenanceTask}
                  onChange={(e) => setNewMaintenanceTask(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <textarea
                  placeholder="Опис роботи"
                  value={newMaintenanceDesc}
                  onChange={(e) => setNewMaintenanceDesc(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={2}
                />
                <input
                  type="date"
                  value={newMaintenanceDate}
                  onChange={(e) => setNewMaintenanceDate(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleAddMaintenance}
                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Додати
                  </button>
                  <button
                    onClick={() => setShowAddMaintenance(false)}
                    className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Скасувати
                  </button>
                </div>
              </div>
            )}

            {vehiclePlans.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Calendar className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>Немає запланованих робіт</p>
              </div>
            ) : (
              <div className="space-y-3">
                {vehiclePlans.map(plan => (
                  <div
                    key={plan.id}
                    className={`bg-white rounded-lg p-4 border ${
                      plan.completed ? 'border-green-200' : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <button
                        onClick={() => onToggleMaintenancePlan(plan.id)}
                        className="mt-1"
                      >
                        {plan.completed ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : (
                          <Circle className="w-5 h-5 text-gray-400" />
                        )}
                      </button>
                      <div className="flex-1">
                        <h4 className={`text-gray-900 mb-1 ${plan.completed ? 'line-through' : ''}`}>
                          {plan.task}
                        </h4>
                        {plan.description && (
                          <p className="text-gray-600 text-sm mb-2">{plan.description}</p>
                        )}
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                          <Calendar className="w-4 h-4" />
                          {new Date(plan.recommendedDate).toLocaleDateString('uk-UA')}
                        </div>
                      </div>
                      <button
                        onClick={() => onDeleteMaintenancePlan(plan.id)}
                        className="text-red-600 hover:text-red-700 p-1"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Comments Tab */}
        {activeTab === 'comments' && (
          <div className="space-y-4">
            <h3 className="text-gray-900">Коментарі флот-менеджера</h3>

            {/* Add Comment */}
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <textarea
                placeholder="Додати коментар..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                rows={3}
              />
              <button
                onClick={handleAddComment}
                disabled={!newComment.trim()}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Додати коментар
              </button>
            </div>

            {/* Comments List */}
            {vehicleComments.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>Немає коментарів</p>
              </div>
            ) : (
              <div className="space-y-3">
                {vehicleComments.map(comment => (
                  <div key={comment.id} className="bg-white rounded-lg p-4 border border-gray-200">
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-gray-900">{comment.authorName}</span>
                      <span className="text-sm text-gray-500">
                        {new Date(comment.createdAt).toLocaleDateString('uk-UA')}
                      </span>
                    </div>
                    <p className="text-gray-700">{comment.text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
