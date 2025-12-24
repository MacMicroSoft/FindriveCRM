import { useState } from 'react';
import { Bell, Check, X, Calendar, DollarSign, AlertCircle, MessageSquare, ArrowLeft } from 'lucide-react';
import { Notification } from '../types';

interface NotificationsProps {
  notifications: Notification[];
  onMarkAsRead: (id: string) => void;
  onDelete: (id: string) => void;
  onBack: () => void;
}

export function Notifications({ notifications, onMarkAsRead, onDelete, onBack }: NotificationsProps) {
  const [showAll, setShowAll] = useState(false);

  const unreadNotifications = notifications.filter(n => !n.read);
  const displayNotifications = showAll ? notifications : notifications.slice(0, 5);

  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'maintenance_reminder':
        return <Calendar className="w-5 h-5 text-blue-600" />;
      case 'expense_added':
        return <DollarSign className="w-5 h-5 text-green-600" />;
      case 'status_change':
        return <AlertCircle className="w-5 h-5 text-orange-600" />;
      case 'message_sent':
        return <MessageSquare className="w-5 h-5 text-purple-600" />;
      default:
        return <Bell className="w-5 h-5 text-gray-600" />;
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 md:px-6">
        <div className="flex items-center justify-between">
          <h1 className="text-gray-900 flex items-center gap-2">
            <Bell className="w-6 h-6" />
            Сповіщення
          </h1>
          {unreadNotifications.length > 0 && (
            <span className="bg-blue-600 text-white text-sm px-3 py-1 rounded-full">
              {unreadNotifications.length}
            </span>
          )}
        </div>
      </div>

      {/* Notifications List */}
      <div className="flex-1 overflow-auto p-4 md:p-6 space-y-3">
        {displayNotifications.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Bell className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Немає сповіщень</p>
          </div>
        ) : (
          <>
            {displayNotifications.map(notification => (
              <div
                key={notification.id}
                className={`bg-white border rounded-lg p-4 ${
                  notification.read ? 'border-gray-200' : 'border-blue-300 bg-blue-50'
                }`}
              >
                <div className="flex gap-3">
                  <div className="flex-shrink-0 mt-1">
                    {getIcon(notification.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h3 className={`${notification.read ? 'text-gray-900' : 'text-gray-900'}`}>
                        {notification.title}
                      </h3>
                      <span className="text-xs text-gray-500 whitespace-nowrap">
                        {new Date(notification.timestamp).toLocaleDateString('uk-UA', {
                          day: 'numeric',
                          month: 'short',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm mb-3">{notification.message}</p>
                    <div className="flex gap-2">
                      {!notification.read && (
                        <button
                          onClick={() => onMarkAsRead(notification.id)}
                          className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                        >
                          <Check className="w-3 h-3" />
                          Позначити прочитаним
                        </button>
                      )}
                      <button
                        onClick={() => onDelete(notification.id)}
                        className="text-xs text-red-600 hover:text-red-700 flex items-center gap-1"
                      >
                        <X className="w-3 h-3" />
                        Видалити
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {notifications.length > 5 && !showAll && (
              <button
                onClick={() => setShowAll(true)}
                className="w-full py-2 text-blue-600 hover:text-blue-700 text-sm"
              >
                Показати всі ({notifications.length})
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
}