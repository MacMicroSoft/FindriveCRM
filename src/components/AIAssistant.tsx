import { Sparkles, AlertTriangle, Wrench, TrendingUp, X, ArrowLeft } from 'lucide-react';
import { AIRecommendation, Vehicle } from '../types';

interface AIAssistantProps {
  recommendations: AIRecommendation[];
  vehicles: Vehicle[];
  onDismiss: (id: string) => void;
  onBack: () => void;
}

export function AIAssistant({ recommendations, vehicles, onDismiss, onBack }: AIAssistantProps) {
  const getIcon = (type: AIRecommendation['type']) => {
    switch (type) {
      case 'maintenance':
        return <Wrench className="w-5 h-5 text-blue-600" />;
      case 'cost_alert':
        return <AlertTriangle className="w-5 h-5 text-orange-600" />;
      case 'efficiency':
        return <TrendingUp className="w-5 h-5 text-green-600" />;
    }
  };

  const getPriorityColor = (priority: AIRecommendation['priority']) => {
    switch (priority) {
      case 'high':
        return 'border-l-4 border-l-red-500';
      case 'medium':
        return 'border-l-4 border-l-orange-500';
      case 'low':
        return 'border-l-4 border-l-blue-500';
    }
  };

  const getPriorityLabel = (priority: AIRecommendation['priority']) => {
    switch (priority) {
      case 'high':
        return 'Високий пріоритет';
      case 'medium':
        return 'Середній пріоритет';
      case 'low':
        return 'Низький пріоритет';
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-4 md:px-6">
        <h1 className="flex items-center gap-2">
          <Sparkles className="w-6 h-6" />
          AI Асистент
        </h1>
        <p className="text-sm text-purple-100 mt-1">
          Розумні рекомендації для вашого автопарку
        </p>
      </div>

      {/* Recommendations List */}
      <div className="flex-1 overflow-auto p-4 md:p-6 space-y-3 bg-gray-50">
        {recommendations.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Sparkles className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Немає активних рекомендацій</p>
            <p className="text-sm mt-1">AI асистент аналізує ваші дані</p>
          </div>
        ) : (
          recommendations.map(recommendation => {
            const vehicle = vehicles.find(v => v.id === recommendation.vehicleId);
            
            return (
              <div
                key={recommendation.id}
                className={`bg-white rounded-lg p-4 ${getPriorityColor(recommendation.priority)}`}
              >
                <div className="flex gap-3">
                  <div className="flex-shrink-0 mt-1">
                    {getIcon(recommendation.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <h3 className="text-gray-900 mb-1">
                          {recommendation.title}
                        </h3>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          recommendation.priority === 'high' 
                            ? 'bg-red-100 text-red-700'
                            : recommendation.priority === 'medium'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}>
                          {getPriorityLabel(recommendation.priority)}
                        </span>
                      </div>
                      <button
                        onClick={() => onDismiss(recommendation.id)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    
                    <p className="text-gray-700 text-sm mb-2">
                      {recommendation.description}
                    </p>

                    {vehicle && (
                      <div className="text-xs text-gray-500 bg-gray-50 px-3 py-2 rounded-lg">
                        {vehicle.brand} {vehicle.model} ({vehicle.licensePlate})
                      </div>
                    )}

                    <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        {new Date(recommendation.createdAt).toLocaleDateString('uk-UA')}
                      </span>
                      <button className="text-xs text-blue-600 hover:text-blue-700">
                        Детальніше →
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}